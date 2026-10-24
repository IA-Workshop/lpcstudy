"""Data generation: trajectories, units, and the splits every experiment uses.

The study needs long, clean time series from three chaotic systems. This
module makes them once per system and packages them in a ``SystemContext``
that the rest of the code (``pipeline``, ``ensemble``, ``oracle``,
``estimation``, ``validation``, ``experiments``, ``analysis``) reads.

Three steps happen here:

1. **Units.** A "statistics orbit" (a long trajectory from the registry start
   state) is used to measure the study's units: the mean and standard
   deviation ``sigma_x`` of the observable, the covariance ``C`` of the state
   (used to "whiten" states, i.e. rescale them so that every direction has
   unit spread), the delay ``tau_d``, the autocorrelation time, and the
   Lyapunov exponent (which sets the time unit, 1 Lyapunov time = 30 steps).
2. **Trajectories.** A main trajectory, and a separate one for training the
   state estimator, start from seed-drawn points of the statistics orbit
   (:func:`draw_starts`) and discard the same burn-in (start-up transient).
   The statistics orbit itself starts at the registry state for every seed,
   so the units do not depend on the seed.
3. **Splits.** The main trajectory (after burn-in) is cut into segments::

       [library segment][gap][construction][gap][calibration][gap][test]

   The library holds the stored past examples of the analog forecaster (CP).
   The construction, calibration and test sets are used to fit rules, tune
   them, and judge them. Each evaluation set holds states thinned by
   ``spacing`` steps and carries a lead of ``(D-1) tau_d`` steps (delay
   history) and a tail of ``H_max`` steps (forecast verification). Gaps
   between segments exceed ``theiler + (D-1) tau_d + H_max``, so no delay
   window or verification window of one set overlaps another set or the
   library (leakage rule L1).

Also here: :func:`make_rng`, the only source of randomness in the package
(every random stream is keyed by the master seed and a text label), and
:func:`sklearn_seed`, which makes seeds acceptable to scikit-learn.
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
from .systems import (
    SYSTEMS,
    OrbitDivergence,
    SystemSpec,
    checked_bound,
    guard_orbit,
    lyapunov_guarded,
    make_flow_step,
    simulate_trajectory,
)

# The three evaluation splits, in the order they lie on the trajectory.
SPLITS: tuple[str, ...] = ("construction", "calibration", "test")


def make_rng(seed: int, *keys: object) -> np.random.Generator:
    """Make a reproducible random generator for one purpose.

    The same ``seed`` and labels always give the same stream, and different
    labels give independent streams, so adding a new random step in one place
    cannot change the numbers drawn in another.

    Parameters
    ----------
    seed : int
        The master seed.
    *keys : object
        Labels (system, split, purpose, ...) mixed into the seed.

    Returns
    -------
    np.random.Generator
        An independent generator for that purpose.
    """
    label = "|".join(str(k) for k in keys).encode()
    return np.random.default_rng([seed, zlib.crc32(label)])


START_PERTURBATION: float = 1e-6
"""``eta``: whitened size of the perturbation of a start state (WU-0002.14, M1).

Fixed by the mathematics check. The perturbation takes about ln(1/eta) = 14
Lyapunov times to saturate, which leaves at least 70 of the 100-LT burn-in.
The basin margin around the attractor (Rossler about 0.015 to 0.02 whitened,
Chua about 0.15 to 0.2) is more than 10^4 eta. Needs owner review before
freeze."""


class Starts(NamedTuple):
    """The seed-drawn start states of the two data trajectories (WU-0002.14).

    Attributes
    ----------
    main_index, estimator_index : int
        The index ``k`` into the post-burn-in statistics orbit.
    main_state, estimator_state : np.ndarray
        The start state ``stats[k] + eta C^{1/2} u``, shape ``(m,)``, float64.
    """

    main_index: int
    main_state: np.ndarray
    estimator_index: int
    estimator_state: np.ndarray


def draw_starts(
    seed: int,
    system: str,
    stats: np.ndarray,
    unwhiten: np.ndarray,
    eta: float = START_PERTURBATION,
) -> Starts:
    """Draw the start states of the main and estimator trajectories.

    One generator ``make_rng(seed, "start", system)`` is consumed in a fixed
    order: ``k_main`` (``integers(0, n)``, an index into the post-burn-in
    statistics orbit), ``u_main`` (``standard_normal(m)``), ``k_est`` and
    ``u_est``. A start is ``stats[k] + eta * (unwhiten @ u)``: a point of the
    sampled invariant measure (the long-run distribution of states), shifted
    by ``eta`` in whitened units in a random direction. The label has no
    embedding dimension, so the robustness contexts of one system share the
    start (common random numbers across ``D``). Needs owner review before
    freeze: it decides which attractor points the study's data come from.

    Parameters
    ----------
    seed : int
        The master seed (``config.seed``); any non-negative integer,
        including a 62-bit one.
    system : str
        The system name (a label of the generator).
    stats : np.ndarray
        The post-burn-in statistics orbit, shape ``(n, m)``.
    unwhiten : np.ndarray
        ``C^{1/2}``, shape ``(m, m)``.
    eta : float, optional
        The whitened perturbation size.

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
    return Starts(
        main_index,
        stats[main_index] + eta * (unwhiten @ main_noise),
        estimator_index,
        stats[estimator_index] + eta * (unwhiten @ estimator_noise),
    )


SKLEARN_SEED_LIMIT: int = 2**32
"""scikit-learn accepts ``random_state`` only in ``[0, 2**32 - 1]``."""


def sklearn_seed(seed: int, label: str) -> int:
    """Make a seed that scikit-learn accepts for ``random_state=`` (DEC-0008 B).

    scikit-learn's ``check_random_state`` raises ``ValueError`` for a seed of
    ``2**32`` or more, and every registered seed DEV-1 to DEV-4 and any
    62-bit confirmatory seed is above that bound (DEF-0010). The raw seed is
    returned when it is in range, so streams of seeds below ``2**32`` (DEV-0)
    are unchanged. Otherwise a 32-bit value is derived from ``make_rng(seed,
    "sklearn", label)``.

    Parameters
    ----------
    seed : int
        The master seed (``config.seed``).
    label : str
        The purpose of the estimator; use one distinct label per
        ``random_state=`` site.

    Returns
    -------
    int
        ``seed`` if ``0 <= seed < 2**32``, else an integer in ``[0, 2**32)``
        that is a deterministic function of ``(seed, label)``.

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
    return int(
        make_rng(int(seed), "sklearn", label).integers(0, SKLEARN_SEED_LIMIT)
    )


@dataclass
class SystemContext:
    """All data about one system that is independent of noise and library size.

    Built once per system by :func:`build_context`. Arrays are float64.

    Attributes
    ----------
    spec : SystemSpec
        The system description (equations, parameters, start state).
    lambda_max : float
        The largest Lyapunov exponent (per natural time unit): the rate at
        which tiny errors grow.
    interval : float
        The observation interval ``Delta``.
    delay : int
        The delay ``tau_d`` in steps.
    embed_dim : int
        The embedding dimension ``D``.
    acf_time : int
        The autocorrelation time of ``x`` in steps (envelope definition, see
        :func:`lpcstudy.embedding.autocorrelation_time`).
    spacing : int
        The thinning interval between sampled states, in steps.
    obs_mean, obs_scale : float
        The mean and the standard deviation ``sigma_x`` of the observable.
    state_mean : np.ndarray
        The mean of the invariant measure.
    whiten, unwhiten : np.ndarray
        ``C^{-1/2}`` and ``C^{1/2}``, the matrices that turn states into
        whitened states and back.
    state_cov : np.ndarray
        The covariance ``C = np.cov(stats.T)`` of the invariant measure that
        was rooted to give ``whiten`` and ``unwhiten`` (kept for the platform
        record, WU-0001.6).
    library_states : np.ndarray
        The latent (hidden) library states, shape ``(L, m)``.
    library_clean : np.ndarray
        The normalized noise-free library observations, shape ``(L,)``.
    library_unit_noise : np.ndarray
        Standard-normal library noise, shape ``(L,)`` (scaled by ``rho``
        later).
    eval_states : np.ndarray
        The latent states of the evaluation trajectory, shape ``(T, m)``.
    eval_clean : np.ndarray
        The normalized noise-free observations of the evaluation trajectory.
    split_indices : dict[str, np.ndarray]
        The time indices (into the evaluation trajectory) of each split.
    estimator_inputs : np.ndarray
        Noise-free delay vectors for training the state estimator ``psi``.
    estimator_targets : np.ndarray
        The whitened latent states at the *start* of each delay window
        (``s_{t-(D-1) tau}``), paired with ``estimator_inputs``. The learned
        estimate initializes a Gauss-Newton refinement in that
        parametrization.
    meta : dict
        Diagnostic information: sizes, timings, and the following.

        * The orbit-guard maxima of DEF-0015: ``lyapunov_orbit_max_abs`` and
          ``trajectory_max_abs`` with the keys ``statistics``, ``main`` and
          ``estimator``, each ``max |x|`` of that orbit, burn-in included.
        * The start states of WU-0002.14: ``start_index`` and ``start_state``
          with the keys ``main`` and ``estimator``, the raw start before the
          burn-in.
        * Since WU-0003.7a, ``main_digest`` and ``estimator_digest``: the
          SHA-256 of the post-burn-in main and estimator trajectories,
          float64, C order, see ``provenance.array_digest``. They decide
          whether two runs followed the same trajectory (the tier of a
          cross-device comparison) and are results leaves through
          ``context_record``.
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
        """Return the delay-window length ``(D-1) tau_d`` in steps."""
        return (self.embed_dim - 1) * self.delay

    def library_admissible(self, size: int, horizon_max: int) -> np.ndarray:
        """List the library indices that may serve as analogs.

        An analog needs a full delay window behind it and ``horizon_max``
        future values ahead of it, so only some library times qualify.

        Parameters
        ----------
        size : int
            The library size ``n_lib``.
        horizon_max : int
            The largest forecast horizon; analogs need that many future
            values.

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
        """Map latent states to whitened coordinates ``C^{-1/2} (s - mean)``."""
        return (states - self.state_mean) @ self.whiten.T


def _symmetric_root(cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(C^{-1/2}, C^{1/2})`` of a symmetric positive-definite matrix.

    Uses the eigendecomposition ``C = V diag(w) V^T``, so the roots are
    ``V diag(w^{-1/2}) V^T`` and ``V diag(w^{1/2}) V^T``.
    """
    eigval, eigvec = np.linalg.eigh(cov)
    root = eigvec @ np.diag(np.sqrt(eigval)) @ eigvec.T
    inv_root = eigvec @ np.diag(1.0 / np.sqrt(eigval)) @ eigvec.T
    return inv_root, root


def lyapunov_record(spec: SystemSpec, cache: Path) -> tuple[float, float]:
    """Get the largest Lyapunov exponent and the orbit maximum (disk-cached).

    The exponent fixes the study's time unit and takes a long trajectory to
    compute, so it is computed once and cached. The cache holds
    ``{name: {"lambda_max": ..., "orbit_max_abs": ...}}``. An entry in that
    form is read without recomputation. A legacy entry (a bare float, written
    before the orbit guard of DEF-0015) is recomputed once under the guard:
    its IEEE bytes must equal the cached value (the regression check of
    DEC-0017 Q1), and the entry is then rewritten in the new form. Needs
    owner review before freeze: it sets the study's time unit.

    Parameters
    ----------
    spec : SystemSpec
        The system description (``orbit_bound`` is required).
    cache : Path
        The JSON file holding previously computed exponents.

    Returns
    -------
    tuple[float, float]
        The exponent per natural time unit and ``max |x|`` over the orbit that
        produced it.

    Raises
    ------
    OrbitDivergence
        If the orbit fails the guard (when computed), or a cached
        ``orbit_max_abs`` exceeds the bound or is not finite.
    RuntimeError
        If the recomputation of a legacy entry differs from it in a single
        bit.
    ValueError
        If the bound is unusable, or the entry is neither a float nor a
        complete new-form entry.
    """
    bound = checked_bound(spec)
    store = json.loads(cache.read_text()) if cache.exists() else {}
    entry = store.get(spec.name)
    if isinstance(entry, dict):
        if set(entry) != {"lambda_max", "orbit_max_abs"} or not all(
            isinstance(v, float) for v in entry.values()
        ):
            raise ValueError(
                f"{cache}: entry '{spec.name}' is malformed: {entry!r}"
            )
        if not entry["orbit_max_abs"] <= bound:  # also refuses NaN
            raise OrbitDivergence(
                f"{cache}: cached orbit max|x| {entry['orbit_max_abs']!r} of "
                f"'{spec.name}' exceeds the bound {bound:g}"
            )
        return entry["lambda_max"], entry["orbit_max_abs"]
    if entry is not None and (
        isinstance(entry, bool) or not isinstance(entry, (int, float))
    ):
        raise ValueError(
            f"{cache}: entry '{spec.name}' is malformed: {entry!r}"
        )
    interval = 20 * spec.max_dt
    lam, largest = lyapunov_guarded(
        spec,
        interval,
        n_steps=spec.lyapunov_steps,
        burn_in=5_000,
    )
    if entry is not None and struct.pack("<d", lam) != struct.pack(
        "<d",
        float(entry),
    ):
        raise RuntimeError(
            f"{cache}: legacy exponent of '{spec.name}' {float(entry)!r} "
            f"differs from the "
            f"recomputation under the orbit guard {lam!r} (a CPU, XLA build or "
            f"code change; "
            "delete the cache entry only after the owner has seen this)"
        )
    store[spec.name] = {"lambda_max": lam, "orbit_max_abs": largest}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(store, indent=2))
    return lam, largest


def build_context(
    system: str,
    config: StudyConfig,
    cache_dir: Path,
    embed_dim: int | None = None,
) -> SystemContext:
    """Generate all trajectories, units and splits for one system.

    Follows the three steps in the module docstring: measure the units on the
    statistics orbit, simulate the seed-drawn main and estimator
    trajectories, and cut the main one into library and evaluation segments.

    Parameters
    ----------
    system : str
        A key of ``SYSTEMS``.
    config : StudyConfig
        The study configuration.
    cache_dir : Path
        The directory for the cached Lyapunov exponents.
    embed_dim : int, optional
        Overrides ``config.embedding_dim`` (robustness sweep).

    Returns
    -------
    SystemContext
        The fully populated context.
    """
    spec = SYSTEMS[system]
    dim = embed_dim or config.embedding_dim
    lam, lyapunov_max = lyapunov_record(spec, cache_dir / "lyapunov.json")
    interval = 1.0 / (config.steps_per_lyapunov * lam)
    step_fn = make_flow_step(spec, spec.params, interval)
    burn = int(config.burn_in_lyapunov * config.steps_per_lyapunov)
    lt_steps = config.steps_per_lyapunov

    # Statistics trajectory: sigma_x, invariant covariance, delay, ACF time. It
    # starts at the registry state for every seed: it defines the units
    # (sigma_x, C, tau_d, spacing, lambda), which are system constants
    # (WU-0002.14, M2); the data trajectories below are seed-drawn.
    stats_full = simulate_trajectory(
        step_fn,
        jnp.asarray(spec.initial_state),
        burn + 200_000,
    )
    stats_max = guard_orbit(
        spec,
        "statistics",
        stats_full,
    )  # burn-in included (DEF-0015)
    stats = stats_full[burn:]
    obs_raw = stats[:, spec.observed_index]
    obs_mean, obs_scale = float(obs_raw.mean()), float(obs_raw.std())
    state_mean = stats.mean(axis=0)
    state_cov = np.cov(stats.T)
    whiten, unwhiten = _symmetric_root(state_cov)
    obs_norm = (obs_raw - obs_mean) / obs_scale
    # tau_d: first AMI minimum, capped so that the delay window (D-1) tau_d
    # spans at most one Lyapunov time (keeps the window inverse problem well
    # conditioned).
    ami_delay = select_delay(obs_norm, max_lag=3 * lt_steps)
    delay = max(1, int(round(min(ami_delay, lt_steps // (dim - 1)))))
    acf_time = autocorrelation_time(obs_norm, max_lag=50 * lt_steps)
    # Phase-coherent systems (Rossler) have a non-decaying ACF envelope; the
    # autocorrelation time is capped at one Lyapunov time (see Methods M4).
    effective_acf = min(acf_time, lt_steps)
    theiler = config.theiler_window
    spacing = max(
        int(math.ceil(config.thinning_factor * effective_acf)),
        theiler,
    )
    history = (dim - 1) * delay
    horizon_max = config.horizon_max
    gap = theiler + history + horizon_max

    library_len = history + max(config.library_sizes) + horizon_max + 1
    split_sizes = {
        "construction": config.n_construction,
        "calibration": config.n_calibration,
        "test": config.n_test,
    }
    offsets: dict[str, np.ndarray] = {}
    cursor = library_len + gap
    for split in SPLITS:
        start = cursor + history
        offsets[split] = start + spacing * np.arange(split_sizes[split])
        cursor = int(offsets[split][-1]) + horizon_max + gap
    total = cursor
    # Seed-drawn starts on the statistics orbit (WU-0002.14, DEF-0017); each
    # data trajectory discards the same burn-in as the statistics orbit, so its
    # first state is a fresh point of the attractor (the perturbation saturates
    # within about 14 LT, M1).
    starts = draw_starts(config.seed, system, stats, unwhiten)
    main_full = simulate_trajectory(
        step_fn,
        jnp.asarray(starts.main_state),
        burn + total,
    )
    main_max = guard_orbit(spec, "main", main_full)  # burn-in included
    main = main_full[burn:]
    library_states = main[:library_len]
    observe = (
        lambda states: (states[:, spec.observed_index] - obs_mean) / obs_scale
    )

    # Separate trajectory for the state estimator (its own seed-drawn start).
    stride = 5
    est_len = history + stride * config.estimator_pairs + 1
    est_full = simulate_trajectory(
        step_fn,
        jnp.asarray(starts.estimator_state),
        burn + est_len,
    )
    est_max = guard_orbit(spec, "estimator", est_full)
    est_traj = est_full[burn:]
    est_obs = observe(est_traj)
    est_idx = history + stride * np.arange(config.estimator_pairs)
    est_inputs = delay_vectors(est_obs, est_idx, delay, dim)
    est_targets = (est_traj[est_idx - history] - state_mean) @ whiten.T

    noise_rng = make_rng(config.seed, system, "library-noise")
    return SystemContext(
        spec=spec,
        lambda_max=lam,
        interval=interval,
        delay=delay,
        embed_dim=dim,
        acf_time=acf_time,
        spacing=spacing,
        obs_mean=obs_mean,
        obs_scale=obs_scale,
        state_mean=state_mean,
        whiten=whiten,
        unwhiten=unwhiten,
        state_cov=state_cov,
        library_states=library_states,
        library_clean=observe(library_states),
        library_unit_noise=noise_rng.standard_normal(library_len),
        eval_states=main,
        eval_clean=observe(main),
        split_indices=offsets,
        estimator_inputs=est_inputs,
        estimator_targets=est_targets,
        meta={
            "lambda_max": lam,
            "interval": interval,
            "delay": delay,
            "ami_delay": ami_delay,
            "embed_dim": dim,
            "acf_time": acf_time,
            "spacing": spacing,
            "obs_scale": obs_scale,
            "trajectory_len": total,
            "library_len": library_len,
            "theiler": theiler,
            "lyapunov_orbit_max_abs": lyapunov_max,
            "trajectory_max_abs": {
                "statistics": stats_max,
                "main": main_max,
                "estimator": est_max,
            },
            "start_index": {
                "main": starts.main_index,
                "estimator": starts.estimator_index,
            },
            "start_state": {
                "main": [float(v) for v in starts.main_state],
                "estimator": [float(v) for v in starts.estimator_state],
            },
            "main_digest": array_digest(main),
            "estimator_digest": array_digest(est_traj),
        },
    )
