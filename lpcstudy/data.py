"""Data generation: trajectories, normalization, whitening and data splits.

Layout of the main trajectory of each system (after burn-in)::

    [library segment][gap][construction][gap][calibration][gap][test]

Each evaluation set holds states thinned by ``spacing`` steps and carries a
lead of ``(D-1) tau_d`` steps (delay history) and a tail of ``H_max`` steps
(forecast verification). Gaps between segments exceed
``theiler + (D-1) tau_d + H_max`` so no delay window or verification window of
one set overlaps another set or the library (leakage rule L1). The state
estimator is trained on a separate trajectory started from a different
initial condition.
"""

from __future__ import annotations

import json
import math
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import jax.numpy as jnp
import numpy as np

from .config import StudyConfig
from .embedding import autocorrelation_time, delay_vectors, select_delay
from .systems import SYSTEMS, SystemSpec, estimate_lyapunov, make_flow_step, \
    simulate_trajectory

SPLITS: tuple[str, ...] = ("construction", "calibration", "test")


def make_rng(seed: int, *keys: object) -> np.random.Generator:
    """Deterministic generator keyed by a master seed and labels.

    Parameters
    ----------
    seed : int
        Master seed.
    *keys : object
        Labels (system, split, purpose, ...) mixed into the seed.

    Returns
    -------
    np.random.Generator
        Independent generator for that purpose.
    """
    label = "|".join(str(k) for k in keys).encode()
    return np.random.default_rng([seed, zlib.crc32(label)])


@dataclass
class SystemContext:
    """Everything about one system that does not depend on noise or library size.

    Attributes
    ----------
    spec : SystemSpec
        System description.
    lambda_max : float
        Largest Lyapunov exponent (per natural time unit).
    interval : float
        Observation interval ``Delta``.
    delay : int
        Delay ``tau_d`` (steps).
    embed_dim : int
        Embedding dimension ``D``.
    acf_time : int
        Autocorrelation time of ``x`` (steps, envelope definition).
    spacing : int
        Thinning interval between sampled states (steps).
    obs_mean, obs_scale : float
        Mean and standard deviation ``sigma_x`` of the observable.
    state_mean : np.ndarray
        Mean of the invariant measure.
    whiten, unwhiten : np.ndarray
        ``C^{-1/2}`` and ``C^{1/2}``.
    library_states : np.ndarray
        Latent library states, shape ``(L, m)``.
    library_clean : np.ndarray
        Normalized noise-free library observations, shape ``(L,)``.
    library_unit_noise : np.ndarray
        Standard-normal library noise, shape ``(L,)`` (scaled by ``rho``).
    eval_states : np.ndarray
        Latent states of the evaluation trajectory, shape ``(T, m)``.
    eval_clean : np.ndarray
        Normalized noise-free observations of the evaluation trajectory.
    split_indices : dict[str, np.ndarray]
        Time indices (into the evaluation trajectory) of each split.
    estimator_inputs : np.ndarray
        Noise-free delay vectors for training ``psi``.
    estimator_targets : np.ndarray
        Whitened latent states at the *start* of each delay window
        (``s_{t-(D-1) tau}``), paired with ``estimator_inputs``; the learned
        estimate initializes a Gauss-Newton refinement in that parametrization.
    meta : dict
        Diagnostic information (sizes, timings).
    """

    spec: SystemSpec
    lambda_max: float
    interval: float
    delay: int
    embed_dim: int
    acf_time: int
    spacing: int
    obs_mean: float
    obs_scale: float
    state_mean: np.ndarray
    whiten: np.ndarray
    unwhiten: np.ndarray
    library_states: np.ndarray
    library_clean: np.ndarray
    library_unit_noise: np.ndarray
    eval_states: np.ndarray
    eval_clean: np.ndarray
    split_indices: dict[str, np.ndarray]
    estimator_inputs: np.ndarray
    estimator_targets: np.ndarray
    meta: dict = field(default_factory=dict)

    @property
    def history(self) -> int:
        """Delay-window length ``(D-1) tau_d`` in steps."""
        return (self.embed_dim - 1) * self.delay

    def library_admissible(self, size: int, horizon_max: int) -> np.ndarray:
        """Admissible analog indices for a library of ``size`` points.

        Parameters
        ----------
        size : int
            Library size ``N``.
        horizon_max : int
            Largest forecast horizon; analogs need that many future values.

        Returns
        -------
        np.ndarray
            Library time indices ``i`` with full history and full future.

        Raises
        ------
        ValueError
            If the stored library is too short.
        """
        indices = np.arange(self.history, self.history + size)
        if indices[-1] + horizon_max >= len(self.library_clean):
            raise ValueError("library segment too short for requested size")
        return indices

    def whiten_states(self, states: np.ndarray) -> np.ndarray:
        """Map latent states to whitened coordinates."""
        return (states - self.state_mean) @ self.whiten.T

    def clean_delays(self, split: str) -> np.ndarray:
        """Noise-free delay vectors of a split, shape ``(n, D)``."""
        return delay_vectors(self.eval_clean, self.split_indices[split],
                             self.delay, self.embed_dim)


def _symmetric_root(cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(C^{-1/2}, C^{1/2})`` of a symmetric positive-definite matrix."""
    eigval, eigvec = np.linalg.eigh(cov)
    root = eigvec @ np.diag(np.sqrt(eigval)) @ eigvec.T
    inv_root = eigvec @ np.diag(1.0 / np.sqrt(eigval)) @ eigvec.T
    return inv_root, root


def lyapunov_cached(spec: SystemSpec, cache: Path) -> float:
    """Largest Lyapunov exponent, cached on disk.

    Parameters
    ----------
    spec : SystemSpec
        System description.
    cache : Path
        JSON file holding previously computed exponents.

    Returns
    -------
    float
        Largest Lyapunov exponent per natural time unit.
    """
    store = json.loads(cache.read_text()) if cache.exists() else {}
    if spec.name not in store:
        interval = 20 * spec.max_dt
        store[spec.name] = estimate_lyapunov(spec, interval, n_steps=100_000,
                                             burn_in=5_000)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(store, indent=2))
    return float(store[spec.name])


def build_context(system: str, config: StudyConfig, cache_dir: Path,
                  embed_dim: int | None = None, delay_scale: float = 1.0
                  ) -> SystemContext:
    """Generate all trajectories and splits for one system.

    Parameters
    ----------
    system : str
        Key of ``SYSTEMS``.
    config : StudyConfig
        Study configuration.
    cache_dir : Path
        Directory for cached Lyapunov exponents.
    embed_dim : int, optional
        Override of ``config.embedding_dim`` (robustness sweep).
    delay_scale : float, optional
        Multiplier applied to the AMI delay (robustness sweep: 0.5).

    Returns
    -------
    SystemContext
        Fully populated context.
    """
    spec = SYSTEMS[system]
    dim = embed_dim or config.embedding_dim
    lam = lyapunov_cached(spec, cache_dir / "lyapunov.json")
    interval = 1.0 / (config.steps_per_lyapunov * lam)
    step_fn = make_flow_step(spec, spec.params, interval)
    burn = int(config.burn_in_lyapunov * config.steps_per_lyapunov)
    lt_steps = config.steps_per_lyapunov

    # Statistics trajectory: sigma_x, invariant covariance, delay, ACF time.
    stats = simulate_trajectory(step_fn, jnp.asarray(spec.initial_state),
                                burn + 200_000)[burn:]
    obs_raw = stats[:, spec.observed_index]
    obs_mean, obs_scale = float(obs_raw.mean()), float(obs_raw.std())
    state_mean = stats.mean(axis=0)
    whiten, unwhiten = _symmetric_root(np.cov(stats.T))
    obs_norm = (obs_raw - obs_mean) / obs_scale
    # tau_d: first AMI minimum, capped so that the delay window (D-1) tau_d spans at
    # most one Lyapunov time (keeps the window inverse problem well conditioned).
    ami_delay = select_delay(obs_norm, max_lag=3 * lt_steps)
    delay = max(1, int(round(min(ami_delay, lt_steps // (dim - 1)) * delay_scale)))
    acf_time = autocorrelation_time(obs_norm, max_lag=50 * lt_steps)
    # Phase-coherent systems (Rossler) have a non-decaying ACF envelope; the
    # autocorrelation time is capped at one Lyapunov time (see Methods M4).
    effective_acf = min(acf_time, lt_steps)
    theiler = config.theiler_window
    spacing = max(int(math.ceil(config.thinning_factor * effective_acf)), theiler)
    history = (dim - 1) * delay
    horizon_max = config.horizon_max
    gap = theiler + history + horizon_max

    library_len = history + max(config.library_sizes) + horizon_max + 1
    split_sizes = {"construction": config.n_construction,
                   "calibration": config.n_calibration, "test": config.n_test}
    offsets: dict[str, np.ndarray] = {}
    cursor = library_len + gap
    for split in SPLITS:
        start = cursor + history
        offsets[split] = start + spacing * np.arange(split_sizes[split])
        cursor = int(offsets[split][-1]) + horizon_max + gap
    total = cursor
    perturbed = np.asarray(spec.initial_state) + 1e-3
    main = simulate_trajectory(step_fn, jnp.asarray(stats[-1]), total)
    library_states = main[:library_len]
    observe = lambda states: (states[:, spec.observed_index] - obs_mean) / obs_scale

    # Separate trajectory for the state estimator (different initial condition).
    stride = 5
    est_len = history + stride * config.estimator_pairs + 1
    est_traj = simulate_trajectory(step_fn, jnp.asarray(perturbed), burn + est_len)[burn:]
    est_obs = observe(est_traj)
    est_idx = history + stride * np.arange(config.estimator_pairs)
    est_inputs = delay_vectors(est_obs, est_idx, delay, dim)
    est_targets = (est_traj[est_idx - history] - state_mean) @ whiten.T

    noise_rng = make_rng(config.seed, system, "library-noise")
    return SystemContext(
        spec=spec, lambda_max=lam, interval=interval, delay=delay, embed_dim=dim,
        acf_time=acf_time, spacing=spacing, obs_mean=obs_mean, obs_scale=obs_scale,
        state_mean=state_mean, whiten=whiten, unwhiten=unwhiten,
        library_states=library_states, library_clean=observe(library_states),
        library_unit_noise=noise_rng.standard_normal(library_len),
        eval_states=main, eval_clean=observe(main), split_indices=offsets,
        estimator_inputs=est_inputs, estimator_targets=est_targets,
        meta={"lambda_max": lam, "interval": interval, "delay": delay, "ami_delay": ami_delay,
              "embed_dim": dim, "acf_time": acf_time, "spacing": spacing,
              "obs_scale": obs_scale, "trajectory_len": total,
              "library_len": library_len, "theiler": theiler},
    )
