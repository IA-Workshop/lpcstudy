"""Data generation: trajectories, normalization, whitening and data splits.

Layout of the main trajectory of each system (after burn-in)::

    [library segment][gap][construction][gap][calibration][gap][test]

Each evaluation set holds states thinned by ``spacing`` steps and carries a
lead of ``(D-1) tau_d`` steps (delay history) and a tail of ``H_max`` steps
(forecast verification). Gaps between segments exceed
``theiler + (D-1) tau_d + H_max`` so no delay window or verification window of
one set overlaps another set or the library (leakage rule L1). The main trajectory and the
separate trajectory on which the state estimator is trained start from seed-drawn points of
the statistics orbit (:func:`draw_starts`) and discard the same burn-in; the statistics
orbit, which defines the units, starts at the registry state for every seed.
"""

from __future__ import annotations

import json
import math
import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

import jax.numpy as jnp
import numpy as np

from .config import StudyConfig
from .embedding import autocorrelation_time, delay_vectors, select_delay
from .provenance import array_digest
from .systems import SYSTEMS, OrbitDivergence, SystemSpec, checked_bound, guard_orbit, \
    lyapunov_guarded, make_flow_step, simulate_trajectory

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


START_PERTURBATION: float = 1e-6
"""``eta``: the whitened size of the perturbation of a start state (WU-0002.14, M1).

Fixed by the mathematics check: the saturation of the perturbation takes about ln(1/eta) = 14
Lyapunov times, leaving at least 70 of the 100-LT burn-in, and the basin margin around the
attractor (Rossler about 0.015 to 0.02 whitened, Chua about 0.15 to 0.2) is more than 10^4 eta.
Needs owner review before freeze."""


class Starts(NamedTuple):
    """The seed-drawn start states of the two data trajectories (WU-0002.14).

    Attributes
    ----------
    main_index, estimator_index : int
        Index ``k`` into the post-burn-in statistics orbit.
    main_state, estimator_state : np.ndarray
        Start state ``stats[k] + eta C^{1/2} u``, shape ``(m,)``, float64.
    """

    main_index: int
    main_state: np.ndarray
    estimator_index: int
    estimator_state: np.ndarray


def draw_starts(seed: int, system: str, stats: np.ndarray, unwhiten: np.ndarray,
                eta: float = START_PERTURBATION) -> Starts:
    """Draw the start states of the main and estimator trajectories of one system.

    One generator ``make_rng(seed, "start", system)`` is consumed in a fixed order: ``k_main``
    (``integers(0, n)``, an index into the post-burn-in statistics orbit), ``u_main``
    (``standard_normal(m)``), ``k_est`` and ``u_est``. A start is ``stats[k] + eta * (unwhiten
    @ u)``: a point of the sampled invariant measure, shifted by ``eta`` in whitened units in a
    random direction. The label has no embedding dimension, so the robustness contexts of one
    system share the start (common random numbers across ``D``). Needs owner review before
    freeze: it decides which attractor points the study's data come from.

    Parameters
    ----------
    seed : int
        Master seed (``config.seed``); any non-negative integer, including a 62-bit one.
    system : str
        System name (a label of the generator).
    stats : np.ndarray
        Post-burn-in statistics orbit, shape ``(n, m)``.
    unwhiten : np.ndarray
        ``C^{1/2}``, shape ``(m, m)``.
    eta : float, optional
        Whitened perturbation size.

    Returns
    -------
    Starts
        The two indices and start states.
    """
    rng = make_rng(seed, "start", system)
    n_states, dim = stats.shape
    main_index = int(rng.integers(0, n_states))
    main_noise = rng.standard_normal(dim)
    estimator_index = int(rng.integers(0, n_states))
    estimator_noise = rng.standard_normal(dim)
    return Starts(main_index, stats[main_index] + eta * (unwhiten @ main_noise),
                  estimator_index, stats[estimator_index] + eta * (unwhiten @ estimator_noise))


SKLEARN_SEED_LIMIT: int = 2**32
"""scikit-learn accepts ``random_state`` only in ``[0, 2**32 - 1]``."""


def sklearn_seed(seed: int, label: str) -> int:
    """Seed for a scikit-learn ``random_state=``, valid in ``[0, 2**32 - 1]`` (DEC-0008 B).

    scikit-learn's ``check_random_state`` raises ``ValueError`` for a seed of ``2**32`` or
    more, and every registered seed DEV-1 to DEV-4 and any 62-bit confirmatory seed is above
    that bound (DEF-0010). The raw seed is returned when it is in range, so streams of
    seeds below ``2**32`` (DEV-0) are unchanged; otherwise a 32-bit value is derived from
    ``make_rng(seed, "sklearn", label)``.

    Parameters
    ----------
    seed : int
        Master seed (``config.seed``).
    label : str
        Purpose of the estimator; use one distinct label per ``random_state=`` site.

    Returns
    -------
    int
        ``seed`` if ``0 <= seed < 2**32``, else an integer in ``[0, 2**32)`` that is a
        deterministic function of ``(seed, label)``.

    Raises
    ------
    TypeError
        If ``seed`` is not an integer.
    ValueError
        If ``seed`` is negative.
    """
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise TypeError(f"seed must be an integer, got {type(seed).__name__}")
    if seed < 0:
        raise ValueError(f"seed must be non-negative, got {seed}")
    if seed < SKLEARN_SEED_LIMIT:
        return int(seed)
    return int(make_rng(int(seed), "sklearn", label).integers(0, SKLEARN_SEED_LIMIT))


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
    state_cov : np.ndarray
        The covariance ``C = np.cov(stats.T)`` of the invariant measure that was rooted to
        give ``whiten`` and ``unwhiten`` (kept for the platform record, WU-0001.6).
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
        Diagnostic information (sizes, timings, the orbit-guard maxima of DEF-0015:
        ``lyapunov_orbit_max_abs`` and ``trajectory_max_abs`` with the keys ``statistics``,
        ``main`` and ``estimator``, each ``max |x|`` of that orbit, burn-in included; and the
        start states of WU-0002.14: ``start_index`` and ``start_state`` with the keys ``main``
        and ``estimator``, the raw start before the burn-in; and, since WU-0003.7a,
        ``main_digest`` and ``estimator_digest``: the SHA-256 of the post-burn-in main and
        estimator trajectories, float64, C order, see ``provenance.array_digest``. They decide
        whether two runs followed the same trajectory (the tier of a cross-device comparison) and
        are results leaves through ``context_record``).
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
    state_cov: np.ndarray
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
            Library size ``n_lib``.
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


def lyapunov_record(spec: SystemSpec, cache: Path) -> tuple[float, float]:
    """Largest Lyapunov exponent and the orbit maximum under the guard, cached on disk.

    The cache holds ``{name: {"lambda_max": ..., "orbit_max_abs": ...}}``. An entry in that form
    is read without recomputation. A legacy entry (a bare float, written before the orbit guard
    of DEF-0015) is recomputed once under the guard: its IEEE bytes must equal the cached value
    (the regression check of DEC-0017 Q1), and the entry is then rewritten in the new form.
    Needs owner review before freeze: it sets the study's time unit.

    Parameters
    ----------
    spec : SystemSpec
        System description (``orbit_bound`` is required).
    cache : Path
        JSON file holding previously computed exponents.

    Returns
    -------
    tuple[float, float]
        The exponent per natural time unit and ``max |x|`` over the orbit that produced it.

    Raises
    ------
    OrbitDivergence
        If the orbit fails the guard (when computed), or a cached ``orbit_max_abs`` exceeds
        the bound or is not finite.
    RuntimeError
        If the recomputation of a legacy entry differs from it in a single bit.
    ValueError
        If the bound is unusable, or the entry is neither a float nor a complete new-form entry.
    """
    bound = checked_bound(spec)
    store = json.loads(cache.read_text()) if cache.exists() else {}
    entry = store.get(spec.name)
    if isinstance(entry, dict):
        if set(entry) != {"lambda_max", "orbit_max_abs"} or not all(
                isinstance(v, float) for v in entry.values()):
            raise ValueError(f"{cache}: entry '{spec.name}' is malformed: {entry!r}")
        if not entry["orbit_max_abs"] <= bound:  # also refuses NaN
            raise OrbitDivergence(f"{cache}: cached orbit max|x| {entry['orbit_max_abs']!r} of "
                                  f"'{spec.name}' exceeds the bound {bound:g}")
        return entry["lambda_max"], entry["orbit_max_abs"]
    if entry is not None and (isinstance(entry, bool) or not isinstance(entry, (int, float))):
        raise ValueError(f"{cache}: entry '{spec.name}' is malformed: {entry!r}")
    interval = 20 * spec.max_dt
    lam, largest = lyapunov_guarded(spec, interval, n_steps=100_000, burn_in=5_000)
    if entry is not None and struct.pack("<d", lam) != struct.pack("<d", float(entry)):
        raise RuntimeError(
            f"{cache}: legacy exponent of '{spec.name}' {float(entry)!r} differs from the "
            f"recomputation under the orbit guard {lam!r} (a CPU, XLA build or code change; "
            "delete the cache entry only after the owner has seen this)")
    store[spec.name] = {"lambda_max": lam, "orbit_max_abs": largest}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(store, indent=2))
    return lam, largest


def lyapunov_cached(spec: SystemSpec, cache: Path) -> float:
    """Largest Lyapunov exponent, cached on disk (see ``lyapunov_record``).

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
    return lyapunov_record(spec, cache)[0]


def build_context(system: str, config: StudyConfig, cache_dir: Path,
                  embed_dim: int | None = None) -> SystemContext:
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

    Returns
    -------
    SystemContext
        Fully populated context.
    """
    spec = SYSTEMS[system]
    dim = embed_dim or config.embedding_dim
    lam, lyapunov_max = lyapunov_record(spec, cache_dir / "lyapunov.json")
    interval = 1.0 / (config.steps_per_lyapunov * lam)
    step_fn = make_flow_step(spec, spec.params, interval)
    burn = int(config.burn_in_lyapunov * config.steps_per_lyapunov)
    lt_steps = config.steps_per_lyapunov

    # Statistics trajectory: sigma_x, invariant covariance, delay, ACF time. It starts at the
    # registry state for every seed: it defines the units (sigma_x, C, tau_d, spacing, lambda),
    # which are system constants (WU-0002.14, M2); the data trajectories below are seed-drawn.
    stats_full = simulate_trajectory(step_fn, jnp.asarray(spec.initial_state), burn + 200_000)
    stats_max = guard_orbit(spec, "statistics", stats_full)  # burn-in included (DEF-0015)
    stats = stats_full[burn:]
    obs_raw = stats[:, spec.observed_index]
    obs_mean, obs_scale = float(obs_raw.mean()), float(obs_raw.std())
    state_mean = stats.mean(axis=0)
    state_cov = np.cov(stats.T)
    whiten, unwhiten = _symmetric_root(state_cov)
    obs_norm = (obs_raw - obs_mean) / obs_scale
    # tau_d: first AMI minimum, capped so that the delay window (D-1) tau_d spans at
    # most one Lyapunov time (keeps the window inverse problem well conditioned).
    ami_delay = select_delay(obs_norm, max_lag=3 * lt_steps)
    delay = max(1, int(round(min(ami_delay, lt_steps // (dim - 1)))))
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
    # Seed-drawn starts on the statistics orbit (WU-0002.14, DEF-0017); each data trajectory
    # discards the same burn-in as the statistics orbit, so its first state is a fresh point of
    # the attractor (the perturbation saturates within about 14 LT, M1).
    starts = draw_starts(config.seed, system, stats, unwhiten)
    main_full = simulate_trajectory(step_fn, jnp.asarray(starts.main_state), burn + total)
    main_max = guard_orbit(spec, "main", main_full)  # burn-in included
    main = main_full[burn:]
    library_states = main[:library_len]
    observe = lambda states: (states[:, spec.observed_index] - obs_mean) / obs_scale

    # Separate trajectory for the state estimator (its own seed-drawn start).
    stride = 5
    est_len = history + stride * config.estimator_pairs + 1
    est_full = simulate_trajectory(step_fn, jnp.asarray(starts.estimator_state), burn + est_len)
    est_max = guard_orbit(spec, "estimator", est_full)
    est_traj = est_full[burn:]
    est_obs = observe(est_traj)
    est_idx = history + stride * np.arange(config.estimator_pairs)
    est_inputs = delay_vectors(est_obs, est_idx, delay, dim)
    est_targets = (est_traj[est_idx - history] - state_mean) @ whiten.T

    noise_rng = make_rng(config.seed, system, "library-noise")
    return SystemContext(
        spec=spec, lambda_max=lam, interval=interval, delay=delay, embed_dim=dim,
        acf_time=acf_time, spacing=spacing, obs_mean=obs_mean, obs_scale=obs_scale,
        state_mean=state_mean, whiten=whiten, unwhiten=unwhiten, state_cov=state_cov,
        library_states=library_states, library_clean=observe(library_states),
        library_unit_noise=noise_rng.standard_normal(library_len),
        eval_states=main, eval_clean=observe(main), split_indices=offsets,
        estimator_inputs=est_inputs, estimator_targets=est_targets,
        meta={"lambda_max": lam, "interval": interval, "delay": delay, "ami_delay": ami_delay,
              "embed_dim": dim, "acf_time": acf_time, "spacing": spacing,
              "obs_scale": obs_scale, "trajectory_len": total,
              "library_len": library_len, "theiler": theiler,
              "lyapunov_orbit_max_abs": lyapunov_max,
              "trajectory_max_abs": {"statistics": stats_max, "main": main_max,
                                     "estimator": est_max},
              "start_index": {"main": starts.main_index, "estimator": starts.estimator_index},
              "start_state": {"main": [float(v) for v in starts.main_state],
                              "estimator": [float(v) for v in starts.estimator_state]},
              "main_digest": array_digest(main), "estimator_digest": array_digest(est_traj)},
    )
