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

import os
import re
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

THREADS_DEFAULT: int = 4
"""Worker threads of a k-d tree query when ``LPC_THREADS`` is unset (as ``tools/run_tests.sh``)."""


def worker_count() -> int:
    """Return the number of worker threads for k-d tree queries from ``LPC_THREADS``.

    The cap is the one the wrappers ``tools/run_tests.sh`` and ``tools/run_preset.sh``
    export (DEF-0012, RSRC.11): an integer from 1 to 99, read at each call; unset or empty
    means 4, as the shell expression ``${LPC_THREADS:-4}`` does there. The worker count
    changes the speed of a query and no value it returns.

    Returns
    -------
    int
        The worker count.

    Raises
    ------
    ValueError
        If ``LPC_THREADS`` is set and is not an integer from 1 to 99 (no fallback, PRIME.4).
    """
    text = os.environ.get("LPC_THREADS", "")
    if text == "":
        return THREADS_DEFAULT
    if re.fullmatch(r"[1-9][0-9]?", text) is None:
        raise ValueError(f"LPC_THREADS must be an integer from 1 to 99, got {text!r}")
    return int(text)

DRAW_COUNTERS: tuple[str, ...] = (
    "invariant_mean_replacements", "nu_replacements", "gain_replacements", "gain_floor",
    "error_clips_plp_href", "error_clips_nonfinite_href")
"""Columns of the per-state ``handled`` array of a computation (DEF-0001, WU-0002.11a).

Each column counts (state, draw) pairs and is invariant under a row subset *and* a horizon
subset of the moments (D1 of the mathematics review, option (b)): the first four are
horizon-free (an estimate, or the gains of an estimate), the last two are taken at ``H_ref``,
which every horizon set contains. ``gain_*`` are filled by ``evaluation_draws`` only.
"""

ENTRY_COUNTERS: tuple[str, ...] = ("error_clips_cp", "error_clips_plp", "error_clips_nonfinite")
"""Totals over (state, draw, horizon) error entries; they depend on the horizon set, so they are
not columns of ``handled`` and are dropped by every state or horizon subset (``clip_entries``)."""

DRAW_COLUMN: dict[str, int] = {name: i for i, name in enumerate(DRAW_COUNTERS)}


@dataclass(frozen=True)
class ClipMasks:
    """Which error entries ``clip_errors`` clipped, on the pre-clip values.

    Attributes
    ----------
    cp, plp, nonfinite : np.ndarray
        Boolean arrays shaped like the errors. ``cp``: a CP error with ``|e| > clip``.
        ``plp``: a finite PLP error with ``|e| > clip``. ``nonfinite``: a PLP error that is
        NaN or infinite (replaced by ``+clip`` for NaN and +inf, ``-clip`` for -inf). The three
        are disjoint, and an error of exactly ``+-clip`` is in none.
    """

    cp: np.ndarray
    plp: np.ndarray
    nonfinite: np.ndarray

    def counts(self) -> dict[str, int]:
        """Entry counts ``error_clips_cp``, ``_plp``, ``_nonfinite`` and their sum ``error_clips``."""
        out = {"error_clips_cp": int(self.cp.sum()), "error_clips_plp": int(self.plp.sum()),
               "error_clips_nonfinite": int(self.nonfinite.sum())}
        out["error_clips"] = sum(out.values())
        return out


def clip_errors(cp: np.ndarray, plp: np.ndarray, truth: np.ndarray, clip: float = ERROR_CLIP
                ) -> tuple[np.ndarray, np.ndarray, ClipMasks]:
    """Errors against the noise-free truth, clipped at ``+-clip`` and counted (E1 to E3).

    The values are those of the original three lines, in the same order: CP is ``np.clip`` of
    ``cp - truth``; PLP is ``nan_to_num`` (NaN and +inf to ``+clip``, -inf to ``-clip``) and
    then ``np.clip``. A NaN CP error is not clipped (``np.clip`` keeps it) and so is not
    counted; it would propagate visibly. The clip is part of the estimand (v3 section 4), so
    the counts are reported, not acted on.

    Parameters
    ----------
    cp, plp : np.ndarray
        Forecasts, ``(n, M, nH)``.
    truth : np.ndarray
        Noise-free truth, broadcastable to the forecasts (``(n, 1, nH)``).
    clip : float, optional
        Clip level in units of ``sigma_x``.

    Returns
    -------
    cp_err, plp_err : np.ndarray
        Clipped errors.
    masks : ClipMasks
        The entries that were clipped, from the pre-clip values.
    """
    cp_raw = cp - truth
    plp_raw = plp - truth
    cp_err = np.clip(cp_raw, -clip, clip)
    plp_err = np.nan_to_num(plp_raw, nan=clip, posinf=clip, neginf=-clip)
    plp_err = np.clip(plp_err, -clip, clip)
    finite = np.isfinite(plp_raw)
    masks = ClipMasks(cp=np.abs(cp_raw) > clip, plp=finite & (np.abs(plp_raw) > clip),
                      nonfinite=~finite)
    return cp_err, plp_err, masks


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
        dist, pos = self.tree.query(vectors, k=n_analogs, workers=worker_count())
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
    handled : np.ndarray or None
        Per-state counts of handled (state, draw) pairs, ``(n, len(DRAW_COUNTERS))`` int64
        (``gain_*`` columns are 0 here; ``evaluation_draws`` fills them).
    clip_entries : dict[str, int] or None
        ``error_clips_cp``, ``_plp``, ``_nonfinite`` totals of this batch (``ENTRY_COUNTERS``).
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
    handled: np.ndarray | None = None
    clip_entries: dict[str, int] | None = None


def forecast_draws(setup: ForecastSetup, library: AnalogLibrary, split: str,
                   states_idx: np.ndarray, unit_noise: np.ndarray,
                   horizons: np.ndarray, reference_horizon: int | None = None) -> DrawBatch:
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
    reference_horizon : int, optional
        ``H_ref`` in steps, for the two ``error_clips_*_href`` columns of ``handled``. With
        ``None`` those two columns are 0 and mean "not computed" (every pipeline caller passes
        the value).

    Returns
    -------
    DrawBatch
        Per-draw errors, seeds, inputs and the handling counts.

    Raises
    ------
    ValueError
        If ``reference_horizon`` is given and is not one of ``horizons``.
    """
    ref_col = None
    if reference_horizon is not None:
        where = np.nonzero(np.asarray(horizons) == reference_horizon)[0]
        if where.size == 0:
            raise ValueError(f"reference_horizon {reference_horizon} is not in the horizons")
        ref_col = int(where[0])
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
    est_phys, est_nu, state_bad, nu_bad = setup.estimator.estimate_counted(flat)
    est_w = ctx.whiten_states(est_phys)
    path = np.asarray(setup.paths(int(horizons[-1]))(jnp.asarray(est_phys)))
    plp = path[:, horizons - 1].reshape(n_states, n_draws, -1)
    est_seed = np.sum((est_w.reshape(n_states, n_draws, -1) - s_true_w[:, None, :]) ** 2,
                      axis=-1)

    cp_err, plp_err, masks = clip_errors(cp, plp, truth[:, None, :])
    handled = np.zeros((n_states, len(DRAW_COUNTERS)), dtype=np.int64)
    handled[:, DRAW_COLUMN["invariant_mean_replacements"]] = \
        state_bad.reshape(n_states, n_draws).sum(axis=1)
    handled[:, DRAW_COLUMN["nu_replacements"]] = nu_bad.reshape(n_states, n_draws).sum(axis=1)
    if ref_col is not None:
        handled[:, DRAW_COLUMN["error_clips_plp_href"]] = masks.plp[:, :, ref_col].sum(axis=1)
        handled[:, DRAW_COLUMN["error_clips_nonfinite_href"]] = \
            masks.nonfinite[:, :, ref_col].sum(axis=1)
    entries = masks.counts()
    return DrawBatch(cp_err=cp_err, plp_err=plp_err, analog_seed_sq=analog_seed,
                     est_seed_sq=est_seed, distance=dist[:, 0].reshape(n_states, n_draws),
                     inputs=noisy, est_states=est_phys.reshape(n_states, n_draws, -1),
                     est_nu=est_nu.reshape(n_states, n_draws),
                     analog_vecs=library.analog_vectors(lib_idx).reshape(n_states, n_draws, dim),
                     handled=handled,
                     clip_entries={k: entries[k] for k in ENTRY_COUNTERS})


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


def draw_correlation(cp_err: np.ndarray, plp_err: np.ndarray
                     ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-state correlation over the noise draws of the CP and PLP errors (H2e, Methods v2 M11).

    Two-pass Pearson over the draw axis: both errors are centered by their own mean first,
    then ``corr = sum(c p) / (sqrt(sum c^2) sqrt(sum p^2))``. The moment formula
    ``(E[cp] - E[c]E[p]) / (sd_c sd_p)`` cancels catastrophically for a nearly constant
    error and is not used. A state whose CP error is constant over the draws (identical
    retrieval for every draw, so the errors are bitwise equal) has no variance, hence no
    correlation: its value is set to exactly 0.0 (Methods v2 section M11) and flagged in
    ``cp_constant``. The same holds for a PLP-constant state (DEC-0011 O2), flagged in
    ``plp_constant``. Constancy is the exact test ``np.ptp(err, axis=1) == 0``. A state that
    is not constant but whose variance underflows gives NaN (counted by the caller, never
    replaced).

    Parameters
    ----------
    cp_err, plp_err : np.ndarray
        Errors against the noise-free truth, both ``(n, M, nH)`` (``M >= 2`` draws).

    Returns
    -------
    corr : np.ndarray
        Correlation, ``(n, nH)``; 0.0 where either error is constant.
    cp_constant, plp_constant : np.ndarray
        Boolean ``(n, nH)``: the CP (PLP) error is constant over the draws.

    Raises
    ------
    ValueError
        If the shapes differ, are not 3-D, or there are fewer than 2 draws.
    """
    if cp_err.shape != plp_err.shape or cp_err.ndim != 3 or cp_err.shape[1] < 2:
        raise ValueError(f"need two (n, M >= 2, nH) arrays of one shape; got {cp_err.shape} "
                         f"and {plp_err.shape}")
    cp_constant = np.ptp(cp_err, axis=1) == 0.0
    plp_constant = np.ptp(plp_err, axis=1) == 0.0
    cp_c = cp_err - cp_err.mean(axis=1, keepdims=True)
    plp_c = plp_err - plp_err.mean(axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = np.sum(cp_c * plp_c, axis=1) / (np.sqrt(np.sum(cp_c**2, axis=1))
                                               * np.sqrt(np.sum(plp_c**2, axis=1)))
    return np.where(cp_constant | plp_constant, 0.0, corr), cp_constant, plp_constant


CORRELATION_FIELDS: tuple[str, ...] = ("err_corr", "cp_constant", "plp_constant")
"""The ``(n, nH)`` fields of ``EnsembleMoments`` that ``draw_correlation`` fills."""


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
    err_corr : np.ndarray or None
        Correlation over the oracle draws of the CP and PLP errors, ``(n, nH)``
        (``draw_correlation``; H2e). ``None`` for moments built without it.
    cp_constant, plp_constant : np.ndarray or None
        Boolean ``(n, nH)``: the CP (PLP) error is constant over the draws, so
        ``err_corr`` was set to 0.0 there.
    handled : np.ndarray or None
        Per-state handling counts ``(n, len(DRAW_COUNTERS))`` int64 (DEF-0001). Every column is
        invariant under a row subset and under the horizon slicing of the sweep views.
        ``None`` for moments built without it (hand-built moments in tests).
    clip_entries : dict[str, int] or None
        ``ENTRY_COUNTERS`` totals over (state, draw, horizon) of the computation that made these
        moments. ``None`` after any subset (a view has no valid totals) and for hand-built moments.
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
    err_corr: np.ndarray | None = None
    cp_constant: np.ndarray | None = None
    plp_constant: np.ndarray | None = None
    handled: np.ndarray | None = None
    clip_entries: dict[str, int] | None = None

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
            kept={k: v[rows] for k, v in self.kept.items()},
            handled=None if self.handled is None else self.handled[rows], clip_entries=None,
            **{k: None if getattr(self, k) is None else getattr(self, k)[rows]
               for k in CORRELATION_FIELDS})


def ensemble_moments(setup: ForecastSetup, library: AnalogLibrary, split: str,
                     unit_noise: np.ndarray, horizons: np.ndarray,
                     keep_horizons: np.ndarray | None = None, keep_draws: int = 0,
                     chunk_traj: int = 6000, reference_horizon: int | None = None
                     ) -> EnsembleMoments:
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
    reference_horizon : int, optional
        ``H_ref`` in steps for the H_ref clip columns of ``handled`` (see ``forecast_draws``).

    Returns
    -------
    EnsembleMoments
        Moments, seeds and the handling counts (``handled`` per state, ``clip_entries`` totals;
        independent of ``chunk_traj``).
    """
    n_states, n_draws, _ = unit_noise.shape
    per_chunk = max(1, chunk_traj // n_draws)
    out = {k: np.zeros((n_states, len(horizons))) for k in
           ("mean_cp", "mean_plp", "sq_cp", "sq_plp", "cross")}
    analog_seed = np.zeros(n_states)
    est_seed = np.zeros(n_states)
    noise_sens = np.zeros(n_states)
    err_corr = np.zeros((n_states, len(horizons)))
    cp_constant = np.zeros((n_states, len(horizons)), dtype=bool)
    plp_constant = np.zeros((n_states, len(horizons)), dtype=bool)
    kept: dict[str, list[np.ndarray]] = {"cp_err": [], "plp_err": [], "inputs": []}
    keep_cols = None if keep_horizons is None else np.searchsorted(horizons, keep_horizons)
    handled = np.zeros((n_states, len(DRAW_COUNTERS)), dtype=np.int64)
    clip_entries = dict.fromkeys(ENTRY_COUNTERS, 0)
    for start in range(0, n_states, per_chunk):
        rows = np.arange(start, min(n_states, start + per_chunk))
        batch = forecast_draws(setup, library, split, rows, unit_noise[rows], horizons,
                               reference_horizon)
        handled[rows] = batch.handled
        for name in ENTRY_COUNTERS:
            clip_entries[name] += batch.clip_entries[name]
        out["mean_cp"][rows] = batch.cp_err.mean(axis=1)
        out["mean_plp"][rows] = batch.plp_err.mean(axis=1)
        out["sq_cp"][rows] = (batch.cp_err**2).mean(axis=1)
        out["sq_plp"][rows] = (batch.plp_err**2).mean(axis=1)
        out["cross"][rows] = (batch.cp_err * batch.plp_err).mean(axis=1)
        analog_seed[rows] = np.sqrt(batch.analog_seed_sq.mean(axis=1))
        est_seed[rows] = np.sqrt(batch.est_seed_sq.mean(axis=1))
        noise_sens[rows] = retrieval_spread(batch.analog_vecs, setup.noise)
        err_corr[rows], cp_constant[rows], plp_constant[rows] = draw_correlation(
            batch.cp_err, batch.plp_err)
        if keep_cols is not None and keep_draws > 0:
            kept["cp_err"].append(batch.cp_err[:, :keep_draws][:, :, keep_cols])
            kept["plp_err"].append(batch.plp_err[:, :keep_draws][:, :, keep_cols])
            kept["inputs"].append(batch.inputs[:, :keep_draws])
    kept_arrays = {k: np.concatenate(v) for k, v in kept.items() if v}
    return EnsembleMoments(horizons=np.asarray(horizons), analog_seed=analog_seed,
                           est_seed=est_seed, noise_sens=noise_sens, kept=kept_arrays,
                           err_corr=err_corr, cp_constant=cp_constant,
                           plp_constant=plp_constant, handled=handled,
                           clip_entries=clip_entries, **out)


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
    handled : np.ndarray or None
        Per-state handling counts ``(n, len(DRAW_COUNTERS))`` int64, including the ``gain_*``
        columns. ``None`` for hand-built draws.
    clip_entries : dict[str, int] or None
        ``ENTRY_COUNTERS`` totals of the computation; ``None`` after a subset.
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
    handled: np.ndarray | None = None
    clip_entries: dict[str, int] | None = None

    def subset(self, rows: np.ndarray) -> "EvaluationDraws":
        """Restrict to a subset of states (``clip_entries`` is dropped; ``None`` stays ``None``)."""
        def pick(name: str, value):
            if name == "horizons":
                return value
            return None if name == "clip_entries" or value is None else value[rows]
        return EvaluationDraws(**{k: pick(k, v) for k, v in self.__dict__.items()})


def sanitize_gains(gains: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Replace non-finite gains of the evaluation draws and flag the draws (inventory sites E5 and D2).

    The values are those of the original line, ``np.nan_to_num(gains, nan=1e300, posinf=1e300)``.
    A draw is *replaced* if any of its gains is not finite, and *floored* if any gain of the
    first ``window`` horizons (the ones ``growth_exponent`` takes the logarithm of) is below the
    ``1e-300`` floor of that logarithm, after the replacement.

    Parameters
    ----------
    gains : np.ndarray
        Amplification ``g_H`` per draw, ``(N, amp_steps)``.
    window : int
        Growth window (steps).

    Returns
    -------
    clean : np.ndarray
        Gains after replacement.
    replaced, floored : np.ndarray
        Boolean ``(N,)``: ``gain_replacements`` and ``gain_floor`` count these draws.
    """
    replaced = ~np.isfinite(gains).all(axis=1)
    clean = np.nan_to_num(gains, nan=1e300, posinf=1e300)
    floored = (clean[:, :window] < 1e-300).any(axis=1)
    return clean, replaced, floored


def evaluation_draws(setup: ForecastSetup, library: AnalogLibrary, split: str,
                     unit_noise: np.ndarray, verify_unit: np.ndarray,
                     horizons: np.ndarray, growth_window: int,
                     synth_unit: np.ndarray, chunk_traj: int = 6000,
                     reference_horizon: int | None = None) -> EvaluationDraws:
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
    reference_horizon : int, optional
        ``H_ref`` in steps for the H_ref clip columns of ``handled`` (see ``forecast_draws``).

    Returns
    -------
    EvaluationDraws
        Errors, deployable features and the handling counts (independent of ``chunk_traj``).
    """
    n_states, n_draws, _ = unit_noise.shape
    per_chunk = max(1, chunk_traj // n_draws)
    parts: dict[str, list[np.ndarray]] = {k: [] for k in (
        "cp_err", "plp_err", "distance", "est_nu", "growth_proxy", "gain_proxy",
        "inputs", "noise_sens", "handled")}
    clip_entries = dict.fromkeys(ENTRY_COUNTERS, 0)
    amp_steps = max(int(horizons[-1]), growth_window)
    amp_fn = setup.amplification(amp_steps)
    for start in range(0, n_states, per_chunk):
        rows = np.arange(start, min(n_states, start + per_chunk))
        batch = forecast_draws(setup, library, split, rows, unit_noise[rows], horizons,
                               reference_horizon)
        flat_states = batch.est_states.reshape(-1, batch.est_states.shape[-1])
        gains = np.asarray(amp_fn(jnp.asarray(flat_states)))
        gains, gain_replaced, gain_floored = sanitize_gains(gains, growth_window)
        shape = (len(rows), n_draws)
        chunk_handled = batch.handled.copy()
        chunk_handled[:, DRAW_COLUMN["gain_replacements"]] = gain_replaced.reshape(shape).sum(1)
        chunk_handled[:, DRAW_COLUMN["gain_floor"]] = gain_floored.reshape(shape).sum(1)
        parts["handled"].append(chunk_handled)
        for name in ENTRY_COUNTERS:
            clip_entries[name] += batch.clip_entries[name]
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
    return EvaluationDraws(horizons=np.asarray(horizons), verify_noise=verify,
                           clip_entries=clip_entries, **merged)
