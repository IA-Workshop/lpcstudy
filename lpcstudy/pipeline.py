"""Study orchestration: cells, rule fitting and evaluation.

Vocabulary
----------
cell
    One (system, noise level, library size, variant) combination.
core cell
    ``rho = 1% sigma_x``, ``n_lib = 10^4``: all splits, all horizons ``1..H_max``.
sweep cell
    Any other (rho, n_lib): test-sweep states only, evaluation horizons only.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .allocation import ErrorPredictor, ProfileProxies, RegimeMap, calibrate_regimes, \
    closed_form_weight, deployable_profile, fit_regime_tree, global_weight, regime_regret, \
    state_horizon_target
from .config import StudyConfig
from .data import SPLITS, SystemContext, build_context, make_rng
from .ensemble import CORRELATION_FIELDS, AnalogLibrary, EnsembleMoments, EvaluationDraws, \
    ForecastSetup, ensemble_moments, evaluation_draws
from .estimation import StateEstimator
from .networks import train_estimator
from .oracle import StateOracles, excess_mse, oracle_weight, realized_horizon, \
    state_oracles
from .statistics import kaplan_meier
from .systems import make_flow_step

LOG = logging.getLogger("lpcstudy")


@dataclass
class SplitData:
    """Oracle moments and evaluation draws of one split in one cell."""

    moments: EnsembleMoments
    evals: EvaluationDraws | None


@dataclass
class Cell:
    """Results of one cell.

    Attributes
    ----------
    system : str
        System name.
    noise : float
        Noise level.
    library_size : int
        Library size.
    label : str
        Variant label (``"base"`` unless a robustness variant).
    setup : ForecastSetup
        Forecasters.
    splits : dict[str, SplitData]
        Data per split (core cells: all three; sweep cells: ``"test"`` only,
        restricted to the test-sweep states).
    oracles : dict[str, StateOracles]
        Oracle state quantities per split (same restriction).
    horizons : np.ndarray
        Horizons at which moments and evaluations are stored.
    """

    system: str
    noise: float
    library_size: int
    label: str
    setup: ForecastSetup
    splits: dict[str, SplitData]
    oracles: dict[str, StateOracles]
    horizons: np.ndarray

    @property
    def ctx(self) -> SystemContext:
        """System context."""
        return self.setup.ctx


@dataclass
class FittedRules:
    """Allocation rules fitted on construction (and calibration) data."""

    proxies: ProfileProxies
    global_weights: np.ndarray
    predictor: ErrorPredictor
    regimes: dict[int, RegimeMap]
    chosen_regimes: int


def allocator_grid(config: StudyConfig) -> np.ndarray:
    """Horizons at which the error-predictor allocator is trained."""
    lt = config.steps_per_lyapunov
    grid = {1, config.horizon_max, *config.eval_horizons,
            *range(lt, config.horizon_max + 1, lt)}
    return np.array(sorted(grid))


class Study:
    """Caches contexts and forecasters and runs cells.

    Parameters
    ----------
    config : StudyConfig
        Study configuration.
    out_dir : Path
        Output directory (caches live in ``out_dir / "cache"``).
    """

    def __init__(self, config: StudyConfig, out_dir: Path) -> None:
        self.config = config
        self.out_dir = out_dir
        self.cache_dir = out_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._contexts: dict[tuple, SystemContext] = {}
        self._setups: dict[tuple, ForecastSetup] = {}
        self._networks: dict[tuple, object] = {}
        self._oracles: dict[tuple, StateOracles] = {}
        self.estimator_log: dict[str, dict] = {}
        self.core_cells: dict[str, Cell] = {}
        self.fitted: dict[str, FittedRules] = {}

    # ------------------------------------------------------------------ setup
    def context(self, system: str, embed_dim: int | None = None) -> SystemContext:
        """System context (cached)."""
        key = (system, embed_dim or self.config.embedding_dim)
        if key not in self._contexts:
            start = time.time()
            self._contexts[key] = build_context(system, self.config, self.cache_dir,
                                                embed_dim)
            LOG.info("context %s built in %.1fs: %s", key, time.time() - start,
                     self._contexts[key].meta)
        return self._contexts[key]

    def setup(self, ctx: SystemContext, noise: float, misspec: float = 0.0,
              n_analogs: int = 1) -> ForecastSetup:
        """Forecasters at one noise level (estimator trained once per noise level)."""
        base_key = (ctx.spec.name, ctx.embed_dim, ctx.delay, noise)
        key = (*base_key, misspec, n_analogs)
        if key in self._setups:
            return self._setups[key]
        network = self._networks.get(base_key)
        if network is None:
            start = time.time()
            network, losses = train_estimator(
                ctx.estimator_inputs, ctx.estimator_targets, noise,
                self.config.estimator_widths, self.config.estimator_epochs,
                self.config.seed + int(1e4 * noise))
            self._networks[base_key] = network
            self.estimator_log[str(base_key)] = {
                "val_loss_by_width": losses, "chosen_width": network.width,
                "seconds": time.time() - start}
            LOG.info("estimator %s trained: %s", base_key, self.estimator_log[str(base_key)])
        params = dict(ctx.spec.params)
        if misspec > 0:
            signs = make_rng(self.config.seed, ctx.spec.name, "misspec").choice(
                [-1.0, 1.0], size=len(params))
            params = {k: v * (1.0 + misspec * s) for (k, v), s in zip(params.items(), signs)}
        model_step = make_flow_step(ctx.spec, params, ctx.interval)
        estimator = StateEstimator(ctx=ctx, network=network, model_step=model_step,
                                   refine_steps=self.config.estimator_refine_steps)
        self._setups[key] = ForecastSetup(ctx=ctx, noise=noise, estimator=estimator,
                                          model_step=model_step, n_analogs=n_analogs)
        return self._setups[key]

    def unit_noise(self, ctx: SystemContext, split: str, purpose: str,
                   n_draws: int, width: int) -> np.ndarray:
        """Standard-normal noise shared across noise levels and library sizes.

        Parameters
        ----------
        ctx : SystemContext
            System context.
        split : str
            Split name.
        purpose : str
            ``"oracle"``, ``"eval"``, ``"verify"`` or ``"convergence"``.
        n_draws : int
            Draws per state.
        width : int
            Trailing dimension (``D`` for query noise, ``H_max`` for verification).

        Returns
        -------
        np.ndarray
            Array ``(n_split, n_draws, width)``.
        """
        rng = make_rng(self.config.seed, ctx.spec.name, ctx.embed_dim, split, purpose)
        n_split = len(ctx.split_indices[split])
        return rng.standard_normal((n_split, n_draws, width))

    def state_oracles(self, ctx: SystemContext, split: str) -> StateOracles:
        """Oracle state quantities (cached; independent of noise and library)."""
        key = (ctx.spec.name, ctx.embed_dim, ctx.delay, split)
        if key not in self._oracles:
            self._oracles[key] = state_oracles(ctx, split, self.config.steps_per_lyapunov)
        return self._oracles[key]

    # ------------------------------------------------------------------ cells
    def run_cell(self, system: str, noise: float, library_size: int, core: bool,
                 with_evals: bool, label: str = "base", embed_dim: int | None = None,
                 misspec: float = 0.0, n_analogs: int = 1) -> Cell:
        """Compute oracle moments (and optionally evaluation draws) for one cell.

        Parameters
        ----------
        system : str
            System name.
        noise : float
            Noise level.
        library_size : int
            Library size.
        core : bool
            Core cell (all splits, horizons ``1..H_max``) or sweep cell
            (test-sweep states, evaluation horizons).
        with_evals : bool
            Also compute evaluation draws (needed wherever rules are evaluated).
        label : str, optional
            Variant label.
        embed_dim : int, optional
            Embedding-dimension override.
        misspec : float, optional
            Relative parameter perturbation of the PLP model.
        n_analogs : int, optional
            CP analog count.

        Returns
        -------
        Cell
            The computed cell.
        """
        cfg = self.config
        start = time.time()
        ctx = self.context(system, embed_dim)
        setup = self.setup(ctx, noise, misspec, n_analogs)
        library = AnalogLibrary.build(ctx, noise, library_size, cfg.horizon_max)
        horizons = np.arange(1, cfg.horizon_max + 1) if core else np.array(cfg.eval_horizons)
        split_names = SPLITS if core else ("test",)
        splits: dict[str, SplitData] = {}
        oracles: dict[str, StateOracles] = {}
        for split in split_names:
            rows = slice(None) if core else slice(0, cfg.n_test_sweep)
            oracle_noise = self.unit_noise(ctx, split, "oracle", cfg.n_oracle_draws,
                                           ctx.embed_dim)[rows]
            keep = allocator_grid(cfg) if (core and split == "construction") else None
            moments = ensemble_moments(setup, library, split, oracle_noise, horizons,
                                       keep_horizons=keep, keep_draws=cfg.allocator_draws)
            evals = None
            if with_evals:
                eval_noise = self.unit_noise(ctx, split, "eval", cfg.n_eval_draws,
                                             ctx.embed_dim)[rows]
                verify = self.unit_noise(ctx, split, "verify", cfg.n_eval_draws,
                                         cfg.horizon_max)[rows]
                synth = self.unit_noise(
                    ctx, split, "noise-sensitivity",
                    cfg.n_eval_draws * cfg.noise_sensitivity_draws, ctx.embed_dim)[rows]
                synth = synth.reshape(synth.shape[0], cfg.n_eval_draws,
                                      cfg.noise_sensitivity_draws, ctx.embed_dim)
                evals = evaluation_draws(setup, library, split, eval_noise, verify,
                                         horizons, cfg.steps_per_lyapunov, synth)
            splits[split] = SplitData(moments=moments, evals=evals)
            full_oracles = self.state_oracles(ctx, split)
            oracles[split] = full_oracles if core else full_oracles.subset(
                np.arange(cfg.n_test_sweep))
        LOG.info("cell %s rho=%.3f n_lib=%d core=%s label=%s done in %.1fs", system, noise,
                 library_size, core, label, time.time() - start)
        return Cell(system=system, noise=noise, library_size=library_size, label=label,
                    setup=setup, splits=splits, oracles=oracles, horizons=horizons)


# ---------------------------------------------------------------------- fitting
def fit_rules(cells: list[Cell], config: StudyConfig) -> FittedRules:
    """Fit A2, A3, the seed proxies and the regime maps on core cells (pooled).

    Parameters
    ----------
    cells : list[Cell]
        Core cells (one for in-system fitting).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    FittedRules
        Fitted rules.
    """
    href_col = config.reference_horizon - 1
    noise = cells[0].noise
    con = [c.splits["construction"] for c in cells]
    cal = [c.splits["calibration"] for c in cells]
    proxies = ProfileProxies.fit(
        np.concatenate([s.evals.distance for s in con]),
        np.concatenate([s.evals.est_nu for s in con]),
        np.concatenate([s.moments.analog_seed for s in con]),
        np.concatenate([s.moments.est_seed for s in con]), noise)

    con_moments = _concat_moments([s.moments for s in con])
    cal_moments = _concat_moments([s.moments for s in cal])
    a2 = global_weight(con_moments)
    predictor = ErrorPredictor.fit(
        con_moments.kept["inputs"], con_moments.kept["cp_err"], con_moments.kept["plp_err"],
        allocator_grid(config), noise, width=64, epochs=config.allocator_epochs,
        seed=config.seed)

    con_profile = np.concatenate([deployable_profile(s.evals, proxies, noise,
                                                     config.steps_per_lyapunov)
                                  for s in con])
    cal_profile = np.concatenate([deployable_profile(s.evals, proxies, noise,
                                                     config.steps_per_lyapunov)
                                  for s in cal])
    cal_evals = _concat_evals([s.evals for s in cal])
    w_target = oracle_weight(con_moments)[:, href_col]
    t_target = np.log(state_horizon_target(con_moments, noise, config.primary_threshold))
    regimes: dict[int, RegimeMap] = {}
    for n_reg in config.regime_counts:
        tree = fit_regime_tree(con_profile, w_target, t_target, n_reg, config.seed)
        regimes[n_reg] = calibrate_regimes(tree, cal_profile, cal_moments, cal_evals,
                                           config.primary_threshold, a2)
    chosen = _choose_regimes(regimes, cal_profile, cal_moments, config)
    return FittedRules(proxies=proxies, global_weights=a2, predictor=predictor,
                       regimes=regimes, chosen_regimes=chosen)


def choose_regime_count(excess_by_count: Mapping[int, float], margin: float = 0.05) -> int:
    """Smallest ``K`` whose calibration excess MSE is within ``margin`` of the minimum (M2 §M7).

    The rule is ``excess_K <= (1.0 + margin) * min_K excess_K`` on the unrounded float64
    values, ``K`` taken in increasing order; a tie at the edge counts as inside. A "tie" is
    defined on this expression with ``min = 1.0`` (``1.0 + 0.05 == 1.05`` in float64),
    not on ``excess - min <= margin * min``, which judges 1.05 against 1.0 as outside
    (DEC-0008 A1, A5). The quantity is the absolute calibration excess
    ``V(w_K) - V(w*)`` (Theorem P1(a)), not the ratio to the best single forecaster.

    Parameters
    ----------
    excess_by_count : Mapping[int, float]
        Mean calibration excess MSE for each candidate ``K``.
    margin : float, optional
        Relative margin (0.05).

    Returns
    -------
    int
        The chosen ``K``.

    Raises
    ------
    ValueError
        If the mapping is empty, ``margin`` is negative, or a value is not finite or is
        negative (the exact excess is non-negative, so a negative value is a bug and
        would invert the margin).
    """
    if margin < 0.0:
        raise ValueError(f"margin must be >= 0, got {margin}")
    if not excess_by_count:
        raise ValueError("choose_regime_count needs at least one candidate K")
    values = {k: float(excess_by_count[k]) for k in sorted(excess_by_count)}
    for count, value in values.items():
        if not np.isfinite(value) or value < 0.0:
            raise ValueError(f"excess MSE for K={count} must be finite and >= 0, got {value}")
    minimum = min(values.values())
    return next(count for count, value in values.items() if value <= (1.0 + margin) * minimum)


def _choose_regimes(regimes: dict[int, RegimeMap], profile: np.ndarray,
                    moments: EnsembleMoments, config: StudyConfig) -> int:
    """``K`` by the §M7 rule on the calibration excess MSE at ``H_ref`` (DEC-0008 A5).

    The candidates are the ``K`` of ``regimes`` up to ``config.regime_max_primary``; the
    horizon column is located by value (``horizons == reference_horizon``).
    """
    column = int(np.nonzero(moments.horizons == config.reference_horizon)[0][0])
    excess = {k: regime_regret(regimes[k], profile, moments, column)[0]
              for k in sorted(regimes) if k <= config.regime_max_primary}
    return choose_regime_count(excess)


def _concat_moments(parts: list[EnsembleMoments]) -> EnsembleMoments:
    """Stack moments of several cells (same horizons)."""
    if len(parts) == 1:
        return parts[0]
    keys = ("mean_cp", "mean_plp", "sq_cp", "sq_plp", "cross", "analog_seed", "est_seed",
            "noise_sens")
    kept_keys = set.intersection(*(set(p.kept) for p in parts))
    correlation = {}
    for key in CORRELATION_FIELDS:  # all parts carry the field, or none does
        present = [getattr(p, key) is not None for p in parts]
        if any(present) and not all(present):
            raise ValueError(f"cannot stack moments: only some carry {key!r}")
        correlation[key] = np.concatenate([getattr(p, key) for p in parts]) if all(present) \
            else None
    return EnsembleMoments(
        horizons=parts[0].horizons,
        kept={k: np.concatenate([p.kept[k] for p in parts]) for k in kept_keys},
        **correlation, **{k: np.concatenate([getattr(p, k) for p in parts]) for k in keys})


def _concat_evals(parts: list[EvaluationDraws]) -> EvaluationDraws:
    """Stack evaluation draws of several cells (same horizons)."""
    if len(parts) == 1:
        return parts[0]
    return EvaluationDraws(**{k: (parts[0].horizons if k == "horizons" else
                                  np.concatenate([getattr(p, k) for p in parts]))
                              for k in parts[0].__dict__})


# ------------------------------------------------------------------- evaluation
def rule_weights(rules: FittedRules, split: SplitData, noise: float,
                 config: StudyConfig, horizons: np.ndarray
                 ) -> dict[str, np.ndarray]:
    """Weights of every rule on one split's evaluation draws.

    Parameters
    ----------
    rules : FittedRules
        Fitted rules.
    split : SplitData
        Split with evaluation draws and oracle moments.
    noise : float
        Noise level of the split (known at deployment).
    config : StudyConfig
        Study configuration.
    horizons : np.ndarray
        Horizons of the split's arrays.

    Returns
    -------
    dict[str, np.ndarray]
        Rule label to weights ``(n, E, nH)``.
    """
    ev = split.evals
    shape = ev.cp_err.shape
    eps_hat, delta_hat = rules.proxies.seeds(ev, noise)
    profile = deployable_profile(ev, rules.proxies, noise, config.steps_per_lyapunov)
    regime_map = rules.regimes[rules.chosen_regimes]
    regime = regime_map.assign(profile)
    moments = split.moments
    oracle_cf = closed_form_weight(moments.analog_seed**2, moments.est_seed**2)
    return {
        "A0": np.ones(shape),
        "A1": np.zeros(shape),
        "A2": np.broadcast_to(rules.global_weights[horizons - 1], shape).copy(),
        "A3": rules.predictor.weights(ev.inputs, horizons),
        "A4": np.broadcast_to(closed_form_weight(eps_hat**2, delta_hat**2)[..., None],
                              shape).copy(),
        "A5": regime_map.weights[regime][..., horizons - 1],
        "A4o": np.broadcast_to(oracle_cf[:, None, None], shape).copy(),
        "A*": np.broadcast_to(oracle_weight(moments)[:, None, :], shape).copy(),
    }


@dataclass
class RuleScores:
    """Scores of one rule on one split.

    Attributes
    ----------
    mse : np.ndarray
        Realized mean squared error per horizon ``(nH,)`` (noise-free truth).
    state_mse_ref : np.ndarray
        Per-state realized squared error at ``H_ref`` averaged over draws ``(n,)``.
    regret : np.ndarray
        Mean exact excess error ``V(w) - V(w*)`` per horizon ``(nH,)`` (Theorem P1(a)).
    agreement : float
        Fraction of decisive states at ``H_ref`` where the rule weights the
        better forecaster more.
    km_median, rmst : float
        Kaplan-Meier median and restricted mean of realized horizons
        (Lyapunov times; ``nan`` if horizons are not contiguous).
    durations, events : np.ndarray
        Realized horizons and event flags ``(n, E)`` (empty if not contiguous).
    """

    mse: np.ndarray
    state_mse_ref: np.ndarray
    regret: np.ndarray
    agreement: float
    km_median: float
    rmst: float
    durations: np.ndarray = field(default_factory=lambda: np.empty(0))
    events: np.ndarray = field(default_factory=lambda: np.empty(0))


def score_rules(weights: dict[str, np.ndarray], split: SplitData, horizons: np.ndarray,
                config: StudyConfig, theta: float) -> dict[str, RuleScores]:
    """Score every rule on a split.

    Parameters
    ----------
    weights : dict[str, np.ndarray]
        Rule weights ``(n, E, nH)``.
    split : SplitData
        Split data.
    horizons : np.ndarray
        Horizons.
    config : StudyConfig
        Study configuration.
    theta : float
        Tolerance for realized horizons.

    Returns
    -------
    dict[str, RuleScores]
        Scores per rule.
    """
    ev, moments = split.evals, split.moments
    ref = int(np.nonzero(horizons == config.reference_horizon)[0][0])
    decisive_ratio = np.sqrt(moments.sq_cp[:, ref] / np.maximum(moments.sq_plp[:, ref],
                                                                 1e-300))
    decisive = np.abs(np.log(decisive_ratio)) >= np.log(1.1)
    cp_better = decisive_ratio < 1.0
    contiguous = np.array_equal(horizons, np.arange(1, len(horizons) + 1))
    lt = config.steps_per_lyapunov
    scores: dict[str, RuleScores] = {}
    for name, w in weights.items():
        err = w * ev.cp_err + (1 - w) * ev.plp_err
        sq = err**2
        regret = np.mean(excess_mse(moments, w), axis=(0, 1))
        favours_cp = w[:, :, ref].mean(axis=1) > 0.5
        agreement = float(np.mean(favours_cp[decisive] == cp_better[decisive])) \
            if decisive.any() else float("nan")
        km_median = rmst = float("nan")
        durations = events = np.empty(0)
        if contiguous:
            durations, events = realized_horizon(err - ev.verify_noise, horizons, theta)
            curve = kaplan_meier(durations, events, len(horizons))
            km_median, rmst = curve.median() / lt, curve.restricted_mean() / lt
        scores[name] = RuleScores(mse=sq.mean(axis=(0, 1)),
                                  state_mse_ref=sq[:, :, ref].mean(axis=1),
                                  regret=regret, agreement=agreement,
                                  km_median=km_median, rmst=rmst,
                                  durations=durations, events=events)
    return scores
