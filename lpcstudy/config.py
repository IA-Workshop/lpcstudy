"""Study configuration: every design constant of the study, in one place.

A "preset" is a named set of choices: how many noise levels to try, how large
the analog libraries are, how many random draws to make, and so on. Keeping
them all in one frozen (unchangeable) object, ``StudyConfig``, means that no
other module hides a number of its own, so a result can always be traced back
to the settings that produced it.

There are three presets:

* ``full`` is the design written in the Methods document, verbatim;
* ``pilot`` shrinks the sample sizes (not the design) so that the whole study
  runs on a 2-core CPU;
* ``smoke`` is tiny and exists only for tests and quick plumbing checks.

``__main__`` picks a preset by name, ``seeds.with_seed`` stamps a master seed
on it, and nearly every other module (``data``, ``pipeline``,
``experiments``, ``analysis``, ``report``) reads its settings from it.
``provenance`` stores a copy of it in every ``results.json``.

Time is measured in observation steps. One Lyapunov time (the time over
which tiny errors grow by a factor of e) is ``steps_per_lyapunov`` = 30
steps, so settings given "in Lyapunov units" are converted by the properties
below.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class StudyConfig:
    """All design constants of the study (a frozen record).

    Frozen means a value cannot be changed after the object is made; to try a
    different setting, build a new object with ``dataclasses.replace``.

    Attributes
    ----------
    name : str
        Preset name (``full``, ``pilot`` or ``smoke``).
    core_systems : tuple[str, ...]
        Systems run through the primary experiments (stages ii-iv).
    steps_per_lyapunov : int
        Observation steps per Lyapunov time. This sets the observation
        interval ``Delta``.
    burn_in_lyapunov : float
        Start-up transient that is thrown away, in Lyapunov times, so the
        trajectory begins on the attractor.
    embedding_dim : int
        Delay-embedding dimension ``D`` (how many past values are stacked).
    theiler_lyapunov : float
        Theiler window, in Lyapunov times. Analogs closer in time than this
        are excluded, because neighbors in time are not independent
        examples.
    thinning_factor : float
        Sampled states are spaced ``thinning_factor`` autocorrelation times
        apart so that they are nearly independent.
    noise_levels : tuple[float, ...]
        Observation-noise standard deviations ``rho``, as fractions of
        ``sigma_x`` (the standard deviation of the observable).
    library_sizes : tuple[int, ...]
        Analog-library sizes ``n_lib`` (number of stored past examples).
    core_noise : float
        Noise level of the core cell (the main noise/library combination).
    core_library : int
        Library size of the core cell.
    library_sweep_noises : tuple[float, ...]
        Noise levels at which the library-size sweep is run.
    horizon_max_lyapunov : float
        Censoring horizon ``H_max``, in Lyapunov times. A forecast is
        followed no further than this.
    eval_horizons_lyapunov : tuple[float, ...]
        Horizons at which blending weights are evaluated, in Lyapunov times.
    reference_horizon_lyapunov : float
        Reference horizon ``H_ref`` for the primary endpoints, in Lyapunov
        times.
    thresholds : tuple[float, ...]
        Candidate error tolerances ``theta`` (fractions of ``sigma_x``).
    primary_threshold : float
        Tolerance used for allocation horizons.
    linear_regime_rms : float
        Small-error regime (assumption A6): the root-mean-square error, as a
        fraction of ``sigma_x``, must be below this for both forecasters
        (used by hypothesis H2a).
    threshold_noise_factor : float
        Validity rule: a tolerance must satisfy ``theta >= factor * rho``,
        with ``factor = 3 * sqrt(2)``.
    n_construction, n_calibration, n_test, n_test_sweep : int
        Number of states in each data split (construction, calibration, test,
        and the smaller test set used in sweeps).
    n_oracle_draws : int
        Noise realizations ``M`` per state used for the oracle quantities
        (the "exact" values computed with knowledge of the truth).
    n_eval_draws : int
        Independent noise realizations per state used for evaluation.
    noise_sensitivity_draws : int
        Synthetic perturbations per evaluation draw used for the deployable
        noise sensitivity ``N_hat`` (a parametric bootstrap of analog
        retrieval).
    convergence_draws : tuple[int, ...]
        Values of ``M`` used in the convergence check (V4).
    convergence_states : int
        Number of states used in the convergence check.
    estimator_pairs : int
        Training pairs for the state estimator ``psi``.
    estimator_widths : tuple[int, ...]
        Hidden-layer widths tried in the capacity check of the learned
        initial guess.
    estimator_refine_steps : int
        Levenberg-Marquardt refinement iterations of ``psi`` (a standard
        least-squares method; this is the model-based step).
    estimator_epochs : int
        Training epochs (passes over the data) for ``psi``.
    allocator_epochs : int
        Training epochs for the error-predictor allocator.
    allocator_draws : int
        Oracle draws per construction state used to train that allocator.
    regime_counts : tuple[int, ...]
        Regime counts ``K`` for the abstraction curve.
    regime_max_primary : int
        Largest ``K`` for the section M7 rule for choosing ``K``.
    bootstrap_resamples : int
        Number of block-bootstrap resamples (used for confidence
        intervals).
    bootstrap_block : int
        Block length (in consecutive states) for the bootstrap.
    misspec_levels : tuple[float, ...]
        Relative parameter perturbations for the misspecification test (how
        wrong the physics model is made on purpose).
    robustness_dims : tuple[int, ...]
        Embedding dimensions in the robustness sweep.
    analog_counts : tuple[int, ...]
        Analog-averaging counts ``k`` (how many neighbors are averaged) in
        the robustness sweep.
    perturbation_scales : tuple[float, ...]
        Finite-perturbation scales (multiples of ``rho``) for ``Lambda_fin``.
    perturbation_dirs : int
        Random directions used for ``Lambda_fin``.
    robustness_systems : tuple[str, ...]
        Systems on which the robustness sweep is run.
    seed : int
        Master random seed.
    seed_id : str
        Id of the seed in ``seeds/development_seeds.json`` (``DEV-n``), or
        ``CONF-1`` for a confirmatory run (LPC.PC.7). The presets use
        ``DEV-0``, whose value is ``seed``.
    """

    name: str = "full"
    core_systems: tuple[str, ...] = ("lorenz63", "rossler", "chua")
    steps_per_lyapunov: int = 30
    burn_in_lyapunov: float = 100.0
    embedding_dim: int = 7
    theiler_lyapunov: float = 1.0
    thinning_factor: float = 5.0
    noise_levels: tuple[float, ...] = (0.005, 0.01, 0.02, 0.05)
    library_sizes: tuple[int, ...] = (1_000, 3_162, 10_000, 31_623, 100_000)
    core_noise: float = 0.01
    core_library: int = 10_000
    library_sweep_noises: tuple[float, ...] = (0.01, 0.02)
    horizon_max_lyapunov: float = 8.0
    eval_horizons_lyapunov: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0, 4.0)
    reference_horizon_lyapunov: float = 1.0
    thresholds: tuple[float, ...] = (0.1, 0.2, 0.3, 0.5)
    primary_threshold: float = 0.2
    linear_regime_rms: float = 0.5
    threshold_noise_factor: float = 4.242640687119285
    n_construction: int = 2000
    n_calibration: int = 1000
    n_test: int = 1000
    n_test_sweep: int = 1000
    n_oracle_draws: int = 200
    n_eval_draws: int = 4
    noise_sensitivity_draws: int = 16
    convergence_draws: tuple[int, ...] = (50, 200, 800)
    convergence_states: int = 100
    estimator_pairs: int = 100_000
    estimator_widths: tuple[int, ...] = (64, 128)
    estimator_refine_steps: int = 15
    estimator_epochs: int = 40
    allocator_epochs: int = 40
    allocator_draws: int = 50
    regime_counts: tuple[int, ...] = (2, 3, 4, 5, 6, 8, 12, 16)
    regime_max_primary: int = 8
    bootstrap_resamples: int = 2000
    bootstrap_block: int = 5
    misspec_levels: tuple[float, ...] = (0.05, 0.10)
    robustness_dims: tuple[int, ...] = (5, 7, 10)
    analog_counts: tuple[int, ...] = (1, 5)
    perturbation_scales: tuple[float, ...] = (1.0, 3.0)
    perturbation_dirs: int = 20
    robustness_systems: tuple[str, ...] = ("lorenz63", "rossler")
    seed: int = 20261005
    seed_id: str = "DEV-0"

    @property
    def horizon_max(self) -> int:
        """Return the censoring horizon ``H_max`` in observation steps."""
        return int(round(self.horizon_max_lyapunov * self.steps_per_lyapunov))

    @property
    def eval_horizons(self) -> tuple[int, ...]:
        """Return the evaluation horizons in observation steps."""
        return tuple(
            int(round(h * self.steps_per_lyapunov))
            for h in self.eval_horizons_lyapunov
        )

    @property
    def reference_horizon(self) -> int:
        """Return the reference horizon ``H_ref`` in observation steps."""
        return int(
            round(self.reference_horizon_lyapunov * self.steps_per_lyapunov)
        )

    @property
    def theiler_window(self) -> int:
        """Return the Theiler window in observation steps."""
        return int(round(self.theiler_lyapunov * self.steps_per_lyapunov))

    def admissible_thresholds(self, noise: float) -> tuple[float, ...]:
        """Keep only the tolerances that are large enough for the noise.

        A tolerance ``theta`` is meaningful only if it is at least
        ``3 sqrt(2) rho``, where ``rho`` is the noise level; a smaller
        tolerance would sit inside the noise. The ``1e-12`` slack stops
        round-off from rejecting a tolerance that equals the bound.

        Parameters
        ----------
        noise : float
            Noise level ``rho`` as a fraction of ``sigma_x``.

        Returns
        -------
        tuple[float, ...]
            The admissible tolerances.
        """
        return tuple(
            t
            for t in self.thresholds
            if t >= self.threshold_noise_factor * noise - 1e-12
        )


FULL = StudyConfig()

PILOT = replace(
    FULL,
    name="pilot",
    n_construction=600,
    n_calibration=300,
    n_test=500,
    n_test_sweep=300,
    n_eval_draws=2,
    convergence_states=40,
    estimator_pairs=40_000,
    estimator_epochs=25,
    allocator_epochs=25,
    allocator_draws=20,
    bootstrap_resamples=500,
    regime_counts=(2, 3, 4, 5, 6, 8, 12),
)

SMOKE = replace(
    FULL,
    name="smoke",
    core_systems=("lorenz63",),
    noise_levels=(0.01, 0.02),
    library_sizes=(1_000, 10_000),
    library_sweep_noises=(0.01,),
    n_construction=120,
    n_calibration=60,
    n_test=80,
    n_test_sweep=60,
    n_oracle_draws=30,
    n_eval_draws=1,
    noise_sensitivity_draws=4,
    convergence_draws=(10, 30),
    convergence_states=10,
    estimator_pairs=5_000,
    estimator_widths=(32,),
    estimator_epochs=3,
    allocator_epochs=3,
    allocator_draws=5,
    regime_counts=(2, 3, 4),
    bootstrap_resamples=50,
    misspec_levels=(0.05,),
    robustness_dims=(7,),
    analog_counts=(1,),
    perturbation_scales=(1.0,),
    perturbation_dirs=4,
    robustness_systems=(),
)

PRESETS: dict[str, StudyConfig] = {"full": FULL, "pilot": PILOT, "smoke": SMOKE}
