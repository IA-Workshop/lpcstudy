"""Study configuration: the single source of truth for every design constant.

The Methods document reproduces the ``full`` preset verbatim. The ``pilot``
preset shrinks sample sizes (not the design) so the whole study runs on a
2-core CPU; the ``smoke`` preset is for tests.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class StudyConfig:
    """All design constants of the study.

    Attributes
    ----------
    name : str
        Preset name.
    core_systems : tuple[str, ...]
        Systems run through the primary experiments (stages ii-iv).
    steps_per_lyapunov : int
        Observation steps per Lyapunov time (sets ``Delta``).
    burn_in_lyapunov : float
        Transient discarded, in Lyapunov times.
    embedding_dim : int
        Delay-embedding dimension ``D``.
    theiler_lyapunov : float
        Theiler window, in Lyapunov times.
    thinning_factor : float
        States are thinned by ``thinning_factor`` autocorrelation times.
    noise_levels : tuple[float, ...]
        Observation-noise standard deviations, as fractions of ``sigma_x``.
    library_sizes : tuple[int, ...]
        Analog-library sizes ``n_lib``.
    core_noise : float
        Noise level of the core cell.
    core_library : int
        Library size of the core cell.
    library_sweep_noises : tuple[float, ...]
        Noise levels at which the library-size sweep is run.
    horizon_max_lyapunov : float
        Censoring horizon ``H_max``, in Lyapunov times.
    eval_horizons_lyapunov : tuple[float, ...]
        Horizons at which weights are evaluated, in Lyapunov times.
    reference_horizon_lyapunov : float
        Reference horizon ``H_ref`` for primary endpoints.
    thresholds : tuple[float, ...]
        Candidate error tolerances ``theta`` (fractions of ``sigma_x``).
    primary_threshold : float
        Tolerance used for allocation horizons.
    linear_regime_rms : float
        Small-error regime (assumption A6): r.m.s. error below this fraction of
        ``sigma_x`` for both forecasters (used by H2a).
    threshold_noise_factor : float
        Validity rule: ``theta >= factor * rho`` (``3 * sqrt(2)``).
    n_construction, n_calibration, n_test, n_test_sweep : int
        State counts per split.
    n_oracle_draws : int
        Noise realizations ``M`` per state for oracle quantities.
    n_eval_draws : int
        Independent noise realizations per state for evaluation.
    noise_sensitivity_draws : int
        Synthetic perturbations per evaluation draw for the deployable noise
        sensitivity ``N_hat`` (parametric bootstrap of analog retrieval).
    convergence_draws : tuple[int, ...]
        ``M`` values for the convergence check (V4).
    convergence_states : int
        States used in the convergence check.
    estimator_pairs : int
        Training pairs for the state estimator ``psi``.
    estimator_widths : tuple[int, ...]
        Hidden widths tried in the capacity check of the learned initial guess.
    estimator_refine_steps : int
        Levenberg-Marquardt refinement iterations of ``psi`` (model-based).
    estimator_epochs : int
        Training epochs for ``psi``.
    allocator_epochs : int
        Training epochs for the error-predictor allocator.
    allocator_draws : int
        Oracle draws per construction state used to train that allocator.
    regime_counts : tuple[int, ...]
        Regime counts ``K`` for the abstraction curve.
    regime_max_primary : int
        Largest ``K`` for the §M7 K rule.
    bootstrap_resamples : int
        Block-bootstrap resamples.
    bootstrap_block : int
        Block length (in consecutive states) for the bootstrap.
    misspec_levels : tuple[float, ...]
        Relative parameter perturbations for the misspecification test.
    robustness_dims : tuple[int, ...]
        Embedding dimensions in the robustness sweep.
    analog_counts : tuple[int, ...]
        Analog-averaging counts ``k`` in the robustness sweep.
    perturbation_scales : tuple[float, ...]
        Finite-perturbation scales (multiples of ``rho``) for ``Lambda_fin``.
    perturbation_dirs : int
        Random directions for ``Lambda_fin``.
    robustness_systems : tuple[str, ...]
        Systems on which the robustness sweep is run.
    seed : int
        Master random seed.
    seed_id : str
        Id of the seed in ``seeds/development_seeds.json`` (``DEV-n``), or ``CONF-1``
        for a confirmatory run (LPC.PC.7). The presets use ``DEV-0``, whose value is
        ``seed``.
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
        """Censoring horizon in observation steps."""
        return int(round(self.horizon_max_lyapunov * self.steps_per_lyapunov))

    @property
    def eval_horizons(self) -> tuple[int, ...]:
        """Evaluation horizons in observation steps."""
        return tuple(int(round(h * self.steps_per_lyapunov))
                     for h in self.eval_horizons_lyapunov)

    @property
    def reference_horizon(self) -> int:
        """Reference horizon in observation steps."""
        return int(round(self.reference_horizon_lyapunov * self.steps_per_lyapunov))

    @property
    def theiler_window(self) -> int:
        """Theiler window in observation steps."""
        return int(round(self.theiler_lyapunov * self.steps_per_lyapunov))

    def admissible_thresholds(self, noise: float) -> tuple[float, ...]:
        """Tolerances satisfying ``theta >= 3 sqrt(2) rho`` at noise ``rho``.

        Parameters
        ----------
        noise : float
            Noise level as a fraction of ``sigma_x``.

        Returns
        -------
        tuple[float, ...]
            Admissible tolerances.
        """
        return tuple(t for t in self.thresholds
                     if t >= self.threshold_noise_factor * noise - 1e-12)


FULL = StudyConfig()

PILOT = replace(
    FULL, name="pilot",
    n_construction=600, n_calibration=300, n_test=500, n_test_sweep=300,
    n_eval_draws=2,
    convergence_states=40, estimator_pairs=40_000, estimator_epochs=25,
    allocator_epochs=25, allocator_draws=20, bootstrap_resamples=500,
    regime_counts=(2, 3, 4, 5, 6, 8, 12),
)

SMOKE = replace(
    FULL, name="smoke", core_systems=("lorenz63",),
    noise_levels=(0.01, 0.02), library_sizes=(1_000, 10_000),
    library_sweep_noises=(0.01,), n_construction=120, n_calibration=60,
    n_test=80, n_test_sweep=60, n_oracle_draws=30, n_eval_draws=1,
    noise_sensitivity_draws=4,
    convergence_draws=(10, 30), convergence_states=10, estimator_pairs=5_000,
    estimator_widths=(32,), estimator_epochs=3, allocator_epochs=3,
    allocator_draws=5, regime_counts=(2, 3, 4), bootstrap_resamples=50,
    misspec_levels=(0.05,), robustness_dims=(7,), analog_counts=(1,),
    perturbation_scales=(1.0,), perturbation_dirs=4, robustness_systems=(),
)

PRESETS: dict[str, StudyConfig] = {"full": FULL, "pilot": PILOT, "smoke": SMOKE}
