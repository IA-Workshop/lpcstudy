"""Forecast ensembles over observation-noise realizations.

For every sampled state ``s_t`` and every noise draw ``r`` the query delay
vector is ``X_t^{(r)} = G(s_t) + rho * z^{(r)}``. From it:

* CP selects analog(s) ``i*`` among the admissible library indices and copies
  their (noisy) futures; the analog latent state is ``a^{(r)} = s_{i*}``.
* PLP estimates ``s_hat^{(r)} = psi(X_t^{(r)})`` and integrates the model.

Errors are taken against the noise-free truth ``h(Phi^H s_t)`` and clipped at
``ERROR_CLIP`` (in units of ``sigma_x``) so that a rare blow-up of an
off-attractor estimate cannot dominate a second moment. The oracle quantities
need only the per-state first and second moments over draws, which are
accumulated chunk by chunk.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import jax.numpy as jnp
import numpy as np
from scipy.spatial import cKDTree

from .data import SystemContext
from .dynamics import make_amplification, make_observation_paths, growth_exponent
from .embedding import delay_vectors
from .estimation import StateEstimator

ERROR_CLIP: float = 10.0


@dataclass
class AnalogLibrary:
    """Nearest-neighbor analog search over admissible library delay vectors.

    Attributes
    ----------
    indices : np.ndarray
        Admissible library time indices.
    noisy_series : np.ndarray
        Noisy normalized library observations.
    tree : cKDTree
        Search tree over the admissible delay vectors.
    """

    indices: np.ndarray
    noisy_series: np.ndarray
    tree: cKDTree

    @classmethod
    def build(cls, ctx: SystemContext, noise: float, size: int, horizon_max: int
              ) -> "AnalogLibrary":
        """Build a library of ``size`` analogs at noise level ``noise``.

        Parameters
        ----------
        ctx : SystemContext
            System context.
        noise : float
            Observation-noise level (fraction of ``sigma_x``).
        size : int
            Library size ``n_lib`` (the first ``n_lib`` admissible points; libraries
            are nested across sizes).
        horizon_max : int
            Largest forecast horizon.

        Returns
        -------
        AnalogLibrary
            The library.
        """
        noisy = ctx.library_clean + noise * ctx.library_unit_noise
        indices = ctx.library_admissible(size, horizon_max)
        vectors = delay_vectors(noisy, indices, ctx.delay, ctx.embed_dim)
        return cls(indices=indices, noisy_series=noisy, tree=cKDTree(vectors))

    def analog_vectors(self, lib_idx: np.ndarray) -> np.ndarray:
        """Delay vectors of selected analogs (averaged over the ``k`` analogs).

        Parameters
        ----------
        lib_idx : np.ndarray
            Library time indices ``(n, k)``.

        Returns
        -------
        np.ndarray
            Mean analog delay vector per query, ``(n, D)``.
        """
        return self.tree.data[lib_idx - self.indices[0]].mean(axis=1)

    def query(self, vectors: np.ndarray, n_analogs: int
              ) -> tuple[np.ndarray, np.ndarray]:
        """Return library time indices and distances of the nearest analogs.

        Parameters
        ----------
        vectors : np.ndarray
            Query delay vectors ``(n, D)``.
        n_analogs : int
            Number of analogs ``k``.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Time indices ``(n, k)`` and distances ``(n, k)``.
        """
        dist, pos = self.tree.query(vectors, k=n_analogs, workers=-1)
        dist = dist.reshape(len(vectors), n_analogs)
        pos = pos.reshape(len(vectors), n_analogs)
        return self.indices[pos], dist


@dataclass
class ForecastSetup:
    """Everything needed to issue CP and PLP forecasts at one noise level.

    Attributes
    ----------
    ctx : SystemContext
        System context.
    noise : float
        Observation-noise level ``rho``.
    estimator : StateEstimator
        State estimator ``psi`` (learned initial guess + model refinement).
    model_step : Callable
        Flow map used by PLP (nominal or misspecified).
    n_analogs : int
        Analogs averaged by CP (``k``).
    """

    ctx: SystemContext
    noise: float
    estimator: StateEstimator
    model_step: Callable
    n_analogs: int = 1
    _paths: dict[int, Callable] = field(default_factory=dict, repr=False)
    _amp: dict[int, Callable] = field(default_factory=dict, repr=False)

    def paths(self, n_steps: int) -> Callable:
        """Compiled PLP observation-path function for ``n_steps`` steps."""
        if n_steps not in self._paths:
            self._paths[n_steps] = make_observation_paths(
                self.model_step, self.ctx.spec.observed_index, self.ctx.obs_mean,
                self.ctx.obs_scale, n_steps)
        return self._paths[n_steps]

    def amplification(self, n_steps: int) -> Callable:
        """Compiled model amplification ``g_H`` function (deployable proxies)."""
        if n_steps not in self._amp:
            self._amp[n_steps] = make_amplification(
                self.model_step, self.ctx.spec.observed_index, self.ctx.obs_scale,
                self.ctx.unwhiten, n_steps)
        return self._amp[n_steps]


@dataclass
class DrawBatch:
    """Per-draw forecasts for a chunk of states.

    Attributes
    ----------
    cp_err, plp_err : np.ndarray
        Errors against the noise-free truth, shape ``(n, M, nH)``.
    analog_seed_sq, est_seed_sq : np.ndarray
        Squared whitened seeds ``||a - s||^2``, ``||s_hat - s||^2``, ``(n, M)``.
    distance : np.ndarray
        Recurrence distance ``R`` (to the nearest analog), ``(n, M)``.
    inputs : np.ndarray
        Noisy delay vectors, ``(n, M, D)``.
    est_states : np.ndarray
        Estimated physical states ``s_hat``, ``(n, M, m)``.
    est_nu : np.ndarray
        Observability factor ``nu`` at the estimate, ``(n, M)``.
    analog_vecs : np.ndarray
        Delay vectors of the retrieved analogs, ``(n, M, D)``.
    """

    cp_err: np.ndarray
    plp_err: np.ndarray
    analog_seed_sq: np.ndarray
    est_seed_sq: np.ndarray
    distance: np.ndarray
    inputs: np.ndarray
    est_states: np.ndarray
    est_nu: np.ndarray
    analog_vecs: np.ndarray


def forecast_draws(setup: ForecastSetup, library: AnalogLibrary, split: str,
                   states_idx: np.ndarray, unit_noise: np.ndarray,
                   horizons: np.ndarray) -> DrawBatch:
    """Issue CP and PLP forecasts for a chunk of states under several noise draws.

    Parameters
    ----------
    setup : ForecastSetup
        Forecasters at one noise level.
    library : AnalogLibrary
        Analog library.
    split : str
        Split name (selects the time indices).
    states_idx : np.ndarray
        Positions within the split, shape ``(n,)``.
    unit_noise : np.ndarray
        Standard-normal query noise, shape ``(n, M, D)``.
    horizons : np.ndarray
        Forecast horizons in steps (sorted, ``>= 1``).

    Returns
    -------
    DrawBatch
        Per-draw errors, seeds and inputs.
    """
    ctx = setup.ctx
    times = ctx.split_indices[split][states_idx]
    n_states, n_draws, dim = unit_noise.shape
    clean = delay_vectors(ctx.eval_clean, times, ctx.delay, ctx.embed_dim)
    noisy = clean[:, None, :] + setup.noise * unit_noise
    flat = noisy.reshape(-1, dim)
    truth = ctx.eval_clean[times[:, None] + horizons[None, :]]  # (n, nH)
    s_true_w = ctx.whiten_states(ctx.eval_states[times])  # (n, m)

    # Context parroting.
    lib_idx, dist = library.query(flat, setup.n_analogs)
    futures = library.noisy_series[lib_idx[:, :, None] + horizons[None, None, :]]
    cp = futures.mean(axis=1).reshape(n_states, n_draws, -1)
    analog_w = ctx.whiten_states(ctx.library_states[lib_idx].mean(axis=1))
    analog_seed = np.sum((analog_w.reshape(n_states, n_draws, -1)
                          - s_true_w[:, None, :]) ** 2, axis=-1)

    # Physics-based latent-state propagation.
    est_phys, est_nu = setup.estimator.estimate(flat)
    est_w = ctx.whiten_states(est_phys)
    path = np.asarray(setup.paths(int(horizons[-1]))(jnp.asarray(est_phys)))
    plp = path[:, horizons - 1].reshape(n_states, n_draws, -1)
    est_seed = np.sum((est_w.reshape(n_states, n_draws, -1) - s_true_w[:, None, :]) ** 2,
                      axis=-1)

    cp_err = np.clip(cp - truth[:, None, :], -ERROR_CLIP, ERROR_CLIP)
    plp_err = np.nan_to_num(plp - truth[:, None, :], nan=ERROR_CLIP,
                            posinf=ERROR_CLIP, neginf=-ERROR_CLIP)
    plp_err = np.clip(plp_err, -ERROR_CLIP, ERROR_CLIP)
    return DrawBatch(cp_err=cp_err, plp_err=plp_err, analog_seed_sq=analog_seed,
                     est_seed_sq=est_seed, distance=dist[:, 0].reshape(n_states, n_draws),
                     inputs=noisy, est_states=est_phys.reshape(n_states, n_draws, -1),
                     est_nu=est_nu.reshape(n_states, n_draws),
                     analog_vecs=library.analog_vectors(lib_idx).reshape(n_states, n_draws, dim))


def retrieval_spread(analog_vecs: np.ndarray, noise: float) -> np.ndarray:
    """Noise sensitivity of analog retrieval (the fourth LPC).

    ``N = sqrt( mean_r ||V_r - mean_r V_r||^2 / D ) / rho``, where ``V_r`` is the
    delay vector of the analog retrieved under noise draw ``r``. ``N = 0`` when
    observation noise never changes the retrieved analog; ``N ~ 1`` when the
    retrieved analog wanders by about one noise standard deviation per coordinate.

    Parameters
    ----------
    analog_vecs : np.ndarray
        Retrieved analog delay vectors ``(..., R, D)`` over ``R`` noise draws.
    noise : float
        Noise level ``rho``.

    Returns
    -------
    np.ndarray
        Noise sensitivity, shape ``(...)``.
    """
    centered = analog_vecs - analog_vecs.mean(axis=-2, keepdims=True)
    dim = analog_vecs.shape[-1]
    return np.sqrt(np.mean(np.sum(centered**2, axis=-1), axis=-1) / dim) / noise


@dataclass
class EnsembleMoments:
    """Per-state moments over oracle noise draws.

    Attributes
    ----------
    horizons : np.ndarray
        Horizons (steps), shape ``(nH,)``.
    mean_cp, mean_plp, sq_cp, sq_plp, cross : np.ndarray
        ``E[e_C]``, ``E[e_P]``, ``E[e_C^2]``, ``E[e_P^2]``, ``E[e_C e_P]``,
        each ``(n, nH)``.
    analog_seed : np.ndarray
        ``epsilon_s`` (r.m.s. whitened analog mismatch), ``(n,)``.
    est_seed : np.ndarray
        ``delta`` (r.m.s. whitened estimation error), ``(n,)``.
    noise_sens : np.ndarray
        Oracle noise sensitivity ``N(s)``: r.m.s. spread over noise draws of the
        retrieved analog's delay vector, per delay coordinate, in units of ``rho``
        (``(n,)``).
    kept : dict[str, np.ndarray]
        Per-draw arrays retained for learned allocators (may be empty).
    """

    horizons: np.ndarray
    mean_cp: np.ndarray
    mean_plp: np.ndarray
    sq_cp: np.ndarray
    sq_plp: np.ndarray
    cross: np.ndarray
    analog_seed: np.ndarray
    est_seed: np.ndarray
    noise_sens: np.ndarray
    kept: dict[str, np.ndarray] = field(default_factory=dict)

    def at(self, horizon: int) -> int:
        """Column index of a horizon."""
        return int(np.nonzero(self.horizons == horizon)[0][0])

    def subset(self, rows: np.ndarray) -> "EnsembleMoments":
        """Restrict to a subset of states."""
        return EnsembleMoments(
            horizons=self.horizons, mean_cp=self.mean_cp[rows],
            mean_plp=self.mean_plp[rows], sq_cp=self.sq_cp[rows],
            sq_plp=self.sq_plp[rows], cross=self.cross[rows],
            analog_seed=self.analog_seed[rows], est_seed=self.est_seed[rows],
            noise_sens=self.noise_sens[rows],
            kept={k: v[rows] for k, v in self.kept.items()})


def ensemble_moments(setup: ForecastSetup, library: AnalogLibrary, split: str,
                     unit_noise: np.ndarray, horizons: np.ndarray,
                     keep_horizons: np.ndarray | None = None, keep_draws: int = 0,
                     chunk_traj: int = 6000) -> EnsembleMoments:
    """Accumulate oracle moments over noise draws, chunk by chunk.

    Parameters
    ----------
    setup : ForecastSetup
        Forecasters.
    library : AnalogLibrary
        Analog library.
    split : str
        Split name.
    unit_noise : np.ndarray
        Standard-normal query noise ``(n, M, D)`` (common random numbers).
    horizons : np.ndarray
        Horizons at which moments are kept.
    keep_horizons : np.ndarray, optional
        Horizons at which per-draw errors are retained (must be a subset of
        ``horizons``); used to train the error-predictor allocator.
    keep_draws : int, optional
        Number of draws per state retained.
    chunk_traj : int, optional
        Maximum number of trajectories integrated at once.

    Returns
    -------
    EnsembleMoments
        Moments and seeds.
    """
    n_states, n_draws, _ = unit_noise.shape
    per_chunk = max(1, chunk_traj // n_draws)
    out = {k: np.zeros((n_states, len(horizons))) for k in
           ("mean_cp", "mean_plp", "sq_cp", "sq_plp", "cross")}
    analog_seed = np.zeros(n_states)
    est_seed = np.zeros(n_states)
    noise_sens = np.zeros(n_states)
    kept: dict[str, list[np.ndarray]] = {"cp_err": [], "plp_err": [], "inputs": []}
    keep_cols = None if keep_horizons is None else np.searchsorted(horizons, keep_horizons)
    for start in range(0, n_states, per_chunk):
        rows = np.arange(start, min(n_states, start + per_chunk))
        batch = forecast_draws(setup, library, split, rows, unit_noise[rows], horizons)
        out["mean_cp"][rows] = batch.cp_err.mean(axis=1)
        out["mean_plp"][rows] = batch.plp_err.mean(axis=1)
        out["sq_cp"][rows] = (batch.cp_err**2).mean(axis=1)
        out["sq_plp"][rows] = (batch.plp_err**2).mean(axis=1)
        out["cross"][rows] = (batch.cp_err * batch.plp_err).mean(axis=1)
        analog_seed[rows] = np.sqrt(batch.analog_seed_sq.mean(axis=1))
        est_seed[rows] = np.sqrt(batch.est_seed_sq.mean(axis=1))
        noise_sens[rows] = retrieval_spread(batch.analog_vecs, setup.noise)
        if keep_cols is not None and keep_draws > 0:
            kept["cp_err"].append(batch.cp_err[:, :keep_draws][:, :, keep_cols])
            kept["plp_err"].append(batch.plp_err[:, :keep_draws][:, :, keep_cols])
            kept["inputs"].append(batch.inputs[:, :keep_draws])
    kept_arrays = {k: np.concatenate(v) for k, v in kept.items() if v}
    return EnsembleMoments(horizons=np.asarray(horizons), analog_seed=analog_seed,
                           est_seed=est_seed, noise_sens=noise_sens, kept=kept_arrays,
                           **out)


@dataclass
class EvaluationDraws:
    """Independent evaluation realizations with deployable features.

    Attributes
    ----------
    horizons : np.ndarray
        Horizons (steps).
    cp_err, plp_err : np.ndarray
        Errors against noise-free truth, ``(n, E, nH)``.
    verify_noise : np.ndarray
        Verification noise ``rho * z`` on the observed truth, ``(n, E, nH)``.
    distance : np.ndarray
        Recurrence distance ``R``, ``(n, E)``.
    est_nu : np.ndarray
        Observability factor at the estimate, ``nu(s_hat)``, ``(n, E)``.
    growth_proxy : np.ndarray
        ``Lambda_hat`` per step from the model at ``s_hat``, ``(n, E)``.
    gain_proxy : np.ndarray
        Model amplification ``g_H(s_hat)`` at ``horizons``, ``(n, E, nH)``.
    inputs : np.ndarray
        Noisy delay vectors, ``(n, E, D)``.
    noise_sens : np.ndarray
        Deployable noise sensitivity ``N_hat`` (parametric bootstrap of analog
        retrieval around the observed delay vector), ``(n, E)``.
    """

    horizons: np.ndarray
    cp_err: np.ndarray
    plp_err: np.ndarray
    verify_noise: np.ndarray
    distance: np.ndarray
    est_nu: np.ndarray
    growth_proxy: np.ndarray
    gain_proxy: np.ndarray
    inputs: np.ndarray
    noise_sens: np.ndarray

    def subset(self, rows: np.ndarray) -> "EvaluationDraws":
        """Restrict to a subset of states."""
        return EvaluationDraws(**{k: (v if k == "horizons" else v[rows])
                                  for k, v in self.__dict__.items()})


def evaluation_draws(setup: ForecastSetup, library: AnalogLibrary, split: str,
                     unit_noise: np.ndarray, verify_unit: np.ndarray,
                     horizons: np.ndarray, growth_window: int,
                     synth_unit: np.ndarray, chunk_traj: int = 6000) -> EvaluationDraws:
    """Forecast errors and deployable features on independent evaluation draws.

    Parameters
    ----------
    setup : ForecastSetup
        Forecasters.
    library : AnalogLibrary
        Analog library.
    split : str
        Split name.
    unit_noise : np.ndarray
        Standard-normal query noise ``(n, E, D)``, independent of the oracle draws.
    verify_unit : np.ndarray
        Standard-normal verification noise ``(n, E, H_max)``.
    horizons : np.ndarray
        Horizons (steps).
    growth_window : int
        Window (steps) for the deployable growth exponent.
    synth_unit : np.ndarray
        Standard-normal synthetic perturbations ``(n, E, K, D)`` for the
        deployable noise sensitivity (parametric bootstrap around each observed
        delay vector).
    chunk_traj : int, optional
        Trajectories per chunk.

    Returns
    -------
    EvaluationDraws
        Errors and deployable features.
    """
    n_states, n_draws, _ = unit_noise.shape
    per_chunk = max(1, chunk_traj // n_draws)
    parts: dict[str, list[np.ndarray]] = {k: [] for k in (
        "cp_err", "plp_err", "distance", "est_nu", "growth_proxy", "gain_proxy",
        "inputs", "noise_sens")}
    amp_steps = max(int(horizons[-1]), growth_window)
    amp_fn = setup.amplification(amp_steps)
    for start in range(0, n_states, per_chunk):
        rows = np.arange(start, min(n_states, start + per_chunk))
        batch = forecast_draws(setup, library, split, rows, unit_noise[rows], horizons)
        flat_states = batch.est_states.reshape(-1, batch.est_states.shape[-1])
        gains = np.asarray(amp_fn(jnp.asarray(flat_states)))
        gains = np.nan_to_num(gains, nan=1e300, posinf=1e300)
        shape = (len(rows), n_draws)
        parts["cp_err"].append(batch.cp_err)
        parts["plp_err"].append(batch.plp_err)
        parts["distance"].append(batch.distance)
        parts["est_nu"].append(batch.est_nu)
        parts["growth_proxy"].append(growth_exponent(gains, growth_window).reshape(shape))
        parts["gain_proxy"].append(gains[:, horizons - 1].reshape(*shape, -1))
        parts["inputs"].append(batch.inputs)
        perturbed = batch.inputs[:, :, None, :] + setup.noise * synth_unit[rows]
        flat_pert = perturbed.reshape(-1, perturbed.shape[-1])
        pert_idx, _ = library.query(flat_pert, setup.n_analogs)
        vecs = library.analog_vectors(pert_idx).reshape(perturbed.shape)
        parts["noise_sens"].append(retrieval_spread(vecs, setup.noise))
    merged = {k: np.concatenate(v) for k, v in parts.items()}
    verify = setup.noise * verify_unit[:, :, horizons - 1]
    return EvaluationDraws(horizons=np.asarray(horizons), verify_noise=verify, **merged)
