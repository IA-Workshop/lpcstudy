"""Study pipeline: build cells, fit allocation rules, score them, count events.

For each chaotic system the study forecasts many starting states with both the
analog forecaster (CP) and the physics-based forecaster (PLP), then asks which
blending weight ``w`` works best. This module is the assembly line for that
work.

* ``Study`` builds (and caches) the system contexts and trained state
  estimators, and runs a *cell*: one forecast experiment at one noise level and
  library size. A cell holds, for every starting state, the oracle moments (the
  mean and mean-square errors that define the best possible weight) and,
  optionally, the evaluation draws (noisy forecasts used to judge deployable
  rules).
* ``fit_rules`` learns the allocation rules (how to choose ``w``) on the
  construction and calibration splits. ``rule_weights`` and ``score_rules``
  apply them to the test split and measure their errors and horizons.
* Every time the code clips, replaces or falls back (PRIME.4), a counter is
  recorded. The ``cell_handling``, ``fit_block`` and related functions gather
  these counts into the ``handling`` block of ``results.json``, so nothing
  happens silently.

``experiments`` calls this module, and ``analysis``, ``clip_sensitivity``,
``report`` and ``dump`` read its results. It calls ``ensemble``, ``oracle``,
``allocation``, ``estimation`` and ``statistics``. Read ``Study.run_cell``
first, then ``fit_rules`` and ``score_rules``.

Vocabulary
----------
cell
    One (system, noise level, library size, variant) combination.
core cell
    ``rho = 1% sigma_x``, ``n_lib = 10^4``: all splits, all horizons
    ``1..H_max``.
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

from .allocation import (
    ErrorPredictor,
    ProfileProxies,
    RegimeMap,
    calibrate_regimes,
    closed_form_floor_count,
    closed_form_weight,
    constant_target_count,
    deployable_profile,
    fit_regime_tree,
    global_weight,
    nu_cap_clip_count,
    pooled_floor_count,
    regime_regret,
    state_horizon_target,
)
from .config import StudyConfig
from .data import SPLITS, SystemContext, build_context, make_rng
from .dump import StateDump
from .ensemble import (
    CORRELATION_FIELDS,
    DRAW_COUNTERS,
    DRAW_COLUMN,
    ENTRY_COUNTERS,
    LM_FIELDS,
    AnalogLibrary,
    EnsembleMoments,
    EvaluationDraws,
    ForecastSetup,
    ensemble_moments,
    evaluation_draws,
    stack_optional,
)
from .estimation import StateEstimator, lm_summary
from .networks import train_estimator
from .oracle import (
    ORACLE_COUNTERS,
    StateOracles,
    curvature,
    excess_mse,
    oracle_weight,
    realized_horizon,
    state_oracles,
)
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
    """The results of one cell (one forecast experiment).

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
        The two forecasters.
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
        """The system context (trajectory, embedding and splits)."""
        return self.setup.ctx


@dataclass
class FittedRules:
    """The allocation rules fitted on construction and calibration data."""

    proxies: ProfileProxies
    global_weights: np.ndarray
    predictor: ErrorPredictor
    regimes: dict[int, RegimeMap]
    chosen_regimes: int
    handled: dict[str, object] = field(default_factory=dict)


def allocator_grid(config: StudyConfig) -> np.ndarray:
    """Return the horizons at which the error-predictor allocator is trained."""
    lt = config.steps_per_lyapunov
    grid = {
        1,
        config.horizon_max,
        *config.eval_horizons,
        *range(lt, config.horizon_max + 1, lt),
    }
    return np.array(sorted(grid))


class Study:
    """Caches contexts and forecasters, and runs cells.

    Building a system context or training a state estimator is slow, so each
    is made once and reused by every cell that needs it. The study also keeps
    the handling records (the counts of clips, replacements and fallbacks)
    that the cells produce.

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
        self._records: dict[tuple[str, str], dict[str, dict]] = {}
        self._fit_records: dict[str, dict] = {}
        self.failed_variants: dict[str, list[str]] = {}
        self.skipped_variants: dict[str, list[str]] = {}
        self.estimator_log: dict[str, dict] = {}
        self.core_cells: dict[str, Cell] = {}
        self.fitted: dict[str, FittedRules] = {}
        # The opt-in state dump (WU-0003.7b); a read-only collector.
        self.dump: StateDump | None = None

    # ------------------------------------------------------------------ setup
    def context(
        self, system: str, embed_dim: int | None = None
    ) -> SystemContext:
        """Return the system context, building it on first use."""
        key = (system, embed_dim or self.config.embedding_dim)
        if key not in self._contexts:
            start = time.time()
            self._contexts[key] = build_context(
                system, self.config, self.cache_dir, embed_dim
            )
            LOG.info(
                "context %s built in %.1fs: %s",
                key,
                time.time() - start,
                self._contexts[key].meta,
            )
        return self._contexts[key]

    def setup(
        self,
        ctx: SystemContext,
        noise: float,
        misspec: float = 0.0,
        n_analogs: int = 1,
    ) -> ForecastSetup:
        """Return the forecasters at one noise level.

        The state estimator (a small neural network) is trained once per noise
        level and shared by every setup at that level.

        Parameters
        ----------
        ctx : SystemContext
            System context.
        noise : float
            Noise level ``rho``.
        misspec : float, optional
            Relative random perturbation of the PLP model parameters (a
            deliberately wrong physics model, for robustness checks).
        n_analogs : int, optional
            Number of analogs CP averages.

        Returns
        -------
        ForecastSetup
            The forecasters.
        """
        base_key = (ctx.spec.name, ctx.embed_dim, ctx.delay, noise)
        key = (*base_key, misspec, n_analogs)
        if key in self._setups:
            return self._setups[key]
        network = self._networks.get(base_key)
        if network is None:
            start = time.time()
            # One fresh stream per width (WU-0002.14; seed code: needs owner
            # review before freeze).
            network, losses = train_estimator(
                ctx.estimator_inputs,
                ctx.estimator_targets,
                noise,
                self.config.estimator_widths,
                self.config.estimator_epochs,
                lambda width: make_rng(
                    self.config.seed,
                    ctx.spec.name,
                    ctx.embed_dim,
                    ctx.delay,
                    "estimator",
                    f"{noise:g}",
                    width,
                ),
            )
            self._networks[base_key] = network
            self.estimator_log[str(base_key)] = {
                "val_loss_by_width": losses,
                "chosen_width": network.width,
                "seconds": time.time() - start,
                "weights_digest": network.weights_digest(),
            }
            LOG.info(
                "estimator %s trained: %s",
                base_key,
                self.estimator_log[str(base_key)],
            )
        params = dict(ctx.spec.params)
        if misspec > 0:
            signs = make_rng(self.config.seed, ctx.spec.name, "misspec").choice(
                [-1.0, 1.0], size=len(params)
            )
            params = {
                k: v * (1.0 + misspec * s)
                for (k, v), s in zip(params.items(), signs)
            }
        model_step = make_flow_step(ctx.spec, params, ctx.interval)
        estimator = StateEstimator(
            ctx=ctx,
            network=network,
            model_step=model_step,
            refine_steps=self.config.estimator_refine_steps,
        )
        self._setups[key] = ForecastSetup(
            ctx=ctx,
            noise=noise,
            estimator=estimator,
            model_step=model_step,
            n_analogs=n_analogs,
        )
        return self._setups[key]

    def unit_noise(
        self,
        ctx: SystemContext,
        split: str,
        purpose: str,
        n_draws: int,
        width: int,
    ) -> np.ndarray:
        """Return standard-normal noise shared across noise levels and sizes.

        The same unit noise is scaled by ``rho`` at each noise level, so
        cells that differ only in ``rho`` or library size see the same random
        numbers (a fair comparison).

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
            Trailing dimension (``D`` for query noise, ``H_max`` for
            verification).

        Returns
        -------
        np.ndarray
            Array ``(n_split, n_draws, width)``.
        """
        rng = make_rng(
            self.config.seed, ctx.spec.name, ctx.embed_dim, split, purpose
        )
        n_split = len(ctx.split_indices[split])
        return rng.standard_normal((n_split, n_draws, width))

    def state_oracles(self, ctx: SystemContext, split: str) -> StateOracles:
        """Return the oracle state quantities (cached; no noise or library)."""
        key = (ctx.spec.name, ctx.embed_dim, ctx.delay, split)
        if key not in self._oracles:
            self._oracles[key] = state_oracles(
                ctx, split, self.config.steps_per_lyapunov, self.config.seed
            )
        return self._oracles[key]

    # ---------------------------------------------------------- handling
    def record_cell(
        self, system: str, label: str, block_id: str, record: dict
    ) -> None:
        """Store the handling record of a cell or check block.

        A block id is stored once; storing it again replaces the old record.

        Parameters
        ----------
        system : str
            System name.
        label : str
            Variant label; ``"base"`` goes to the handling of the system, any
            other label to its robustness handling.
        block_id : str
            Cell id (:func:`cell_id`) or check id (``V3-cp-horizon``,
            ``V4-convergence``).
        record : dict
            Output of :func:`cell_handling` or :func:`check_record`.
        """
        scope = "main" if label == "base" else "robustness"
        self._records.setdefault((system, scope), {})[block_id] = record

    def record_rules(self, system: str, cell: Cell, rules: FittedRules) -> None:
        """Store the evaluation block and fit counters of fitted rules.

        The proxy-dependent counters (D3, D6 of the mathematics review) exist
        only after ``fit_rules``, so they are added to the record of the cell
        here. The fit of the main system goes to its ``fitting`` block; the fit
        of a robustness variant goes inside the record of its cell.

        Parameters
        ----------
        system : str
            System name.
        cell : Cell
            Core cell (already recorded by ``run_cell``).
        rules : FittedRules
            Rules fitted on that cell.

        Raises
        ------
        ValueError
            If the cell was not recorded by ``run_cell``, or the rules carry
            no counters.
        """
        if not rules.handled:
            raise ValueError(
                "record_rules needs rules from fit_rules "
                "(they carry the counters)"
            )
        scope = "main" if cell.label == "base" else "robustness"
        block_id = cell_id(
            cell.label,
            cell.noise,
            cell.library_size,
            "construction" in cell.splits,
        )
        record = self._records.get((system, scope), {}).get(block_id)
        if record is None:
            raise ValueError(
                f"cell {block_id!r} of {system} has no handling record; "
                "it must come from Study.run_cell"
            )
        record["evaluation"] = evaluation_block(cell, rules)
        fit = fit_block(rules, len(cell.horizons))
        if scope == "main":
            self._fit_records[system] = fit
        else:
            record["fitting"] = fit

    def record_skipped_variant(self, system: str, label: str) -> None:
        """Count a robustness variant that was not run (DEF-0025)."""
        self.skipped_variants.setdefault(system, []).append(label)

    def record_failed_variant(self, system: str, label: str) -> None:
        """Count a robustness variant that raised an error.

        The result of the variant keeps its error message.
        """
        self.failed_variants.setdefault(system, []).append(label)

    def _oracle_blocks(self, system: str, main: bool) -> dict[str, dict]:
        """Return the oracle counters of a system's cached state oracles."""
        out = {}
        for (name, embed_dim, _delay, split), oracles in self._oracles.items():
            default = embed_dim == self.config.embedding_dim
            if name == system and default == main:
                key = split if main else f"{split}|D={embed_dim}"
                out[key] = oracle_block(oracles)
        return out

    def system_handling(
        self, system: str, result_counts: dict[str, int]
    ) -> dict:
        """Return the ``handling`` block of one system.

        The schema is ``lpcstudy.handling/2``.

        Parameters
        ----------
        system : str
            System name.
        result_counts : dict[str, int]
            Copy of the counts the hypothesis results already carry
            (``collect_result_counts``).

        Returns
        -------
        dict
            ``schema``, ``cells``, ``oracles``, ``fitting``,
            ``result_counts`` and ``totals`` (every counter of
            ``ALL_COUNTERS`` as an int, the sum over cells, their evaluation
            sub-blocks, the oracles and the fit).
        """
        cells = dict(self._records.get((system, "main"), {}))
        oracles = self._oracle_blocks(system, main=True)
        fitting = self._fit_records.get(system) or empty_fit_block()
        totals = sum_totals([*cells.values(), *oracles.values(), fitting])
        return {
            "schema": HANDLING_SCHEMA,
            "cells": cells,
            "oracles": oracles,
            "fitting": fitting,
            "result_counts": dict(result_counts),
            "totals": totals,
        }

    def robustness_handling(
        self, system: str, result_counts: dict[str, int]
    ) -> dict:
        """Return the handling of one system's robustness variants.

        This is not part of the totals of the system.

        Returns
        -------
        dict
            ``cells`` (variant cells, each with its ``evaluation`` and
            ``fitting``), ``oracles`` (variant embedding dimensions),
            ``result_counts`` and ``totals``.
        """
        cells = dict(self._records.get((system, "robustness"), {}))
        oracles = self._oracle_blocks(system, main=False)
        return {
            "cells": cells,
            "oracles": oracles,
            "result_counts": dict(result_counts),
            "totals": sum_totals([*cells.values(), *oracles.values()]),
        }

    # ------------------------------------------------------------------ cells
    def run_cell(
        self,
        system: str,
        noise: float,
        library_size: int,
        core: bool,
        with_evals: bool,
        label: str = "base",
        embed_dim: int | None = None,
        misspec: float = 0.0,
        n_analogs: int = 1,
    ) -> Cell:
        """Compute oracle moments (and optionally evaluation draws) of a cell.

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
            Also compute evaluation draws (needed wherever rules are
            evaluated).
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
        horizons = (
            np.arange(1, cfg.horizon_max + 1)
            if core
            else np.array(cfg.eval_horizons)
        )
        split_names = SPLITS if core else ("test",)
        splits: dict[str, SplitData] = {}
        oracles: dict[str, StateOracles] = {}
        for split in split_names:
            rows = slice(None) if core else slice(0, cfg.n_test_sweep)
            oracle_noise = self.unit_noise(
                ctx, split, "oracle", cfg.n_oracle_draws, ctx.embed_dim
            )[rows]
            keep = (
                allocator_grid(cfg)
                if (core and split == "construction")
                else None
            )
            halves = (
                {}
                if (
                    self.dump is not None
                    and split == "test"
                    and label == "base"
                )
                else None
            )
            moments = ensemble_moments(
                setup,
                library,
                split,
                oracle_noise,
                horizons,
                keep_horizons=keep,
                keep_draws=cfg.allocator_draws,
                reference_horizon=cfg.reference_horizon,
                half_out=halves,
            )
            if halves is not None:  # a copy of sums of the same draws
                self.dump.record_halves(
                    system, noise, library_size, core, horizons, halves
                )
            evals = None
            if with_evals:
                eval_noise = self.unit_noise(
                    ctx, split, "eval", cfg.n_eval_draws, ctx.embed_dim
                )[rows]
                verify = self.unit_noise(
                    ctx, split, "verify", cfg.n_eval_draws, cfg.horizon_max
                )[rows]
                synth = self.unit_noise(
                    ctx,
                    split,
                    "noise-sensitivity",
                    cfg.n_eval_draws * cfg.noise_sensitivity_draws,
                    ctx.embed_dim,
                )[rows]
                synth = synth.reshape(
                    synth.shape[0],
                    cfg.n_eval_draws,
                    cfg.noise_sensitivity_draws,
                    ctx.embed_dim,
                )
                evals = evaluation_draws(
                    setup,
                    library,
                    split,
                    eval_noise,
                    verify,
                    horizons,
                    cfg.steps_per_lyapunov,
                    synth,
                    reference_horizon=cfg.reference_horizon,
                )
            splits[split] = SplitData(moments=moments, evals=evals)
            full_oracles = self.state_oracles(ctx, split)
            oracles[split] = (
                full_oracles
                if core
                else full_oracles.subset(np.arange(cfg.n_test_sweep))
            )
        self.record_cell(
            system,
            label,
            cell_id(label, noise, library_size, core),
            cell_handling(
                splits,
                cfg.n_oracle_draws,
                cfg.reference_horizon,
                noise,
                ctx.embed_dim - ctx.spec.dim,
            ),
        )
        LOG.info(
            "cell %s rho=%.3f n_lib=%d core=%s label=%s done in %.1fs",
            system,
            noise,
            library_size,
            core,
            label,
            time.time() - start,
        )
        return Cell(
            system=system,
            noise=noise,
            library_size=library_size,
            label=label,
            setup=setup,
            splits=splits,
            oracles=oracles,
            horizons=horizons,
        )


# ------------------------------------------------- handling counters
def moment_counters(
    moments: EnsembleMoments, reference_horizon: int
) -> dict[str, int]:
    """Count special cases in the stored moment arrays (DEF-0001).

    These counters come from the stored arrays, so no instrumentation is
    needed.

    * ``zero_variance_corr``: moment entries (state, horizon) whose CP **or**
      PLP error is constant over the oracle draws, so the correlation was set
      to 0 (the union D4 of the mathematics review); ``_cp`` and ``_plp`` are
      its parts, so ``zero_variance_corr == _cp + _plp - both``. It counts all
      horizons; the ``H_ref`` slice is the one H2e reports.
    * ``curvature_floor``: entries with ``c = E[(e_C - e_P)^2] < 1e-300`` (the
      expression of ``oracle.curvature``, so negatives from cancellation
      count); under P1(a) ``c >= rho^2 / k``, so this is a sentinel (an alarm
      that should never ring).
    * ``decisive_floor``: states with ``E[e_P^2] < 1e-300`` at ``H_ref`` (the
      floor of the decisive ratio in ``score_rules``); also a sentinel.

    Parameters
    ----------
    moments : EnsembleMoments
        Oracle moments of a cell split, built by ``ensemble_moments`` (they
        carry the masks).
    reference_horizon : int
        ``H_ref`` in steps.

    Returns
    -------
    dict[str, int]
        The five counters.

    Raises
    ------
    ValueError
        If the moments carry no ``cp_constant`` and ``plp_constant``, or
        ``H_ref`` is not among the horizons.
    """
    if moments.cp_constant is None or moments.plp_constant is None:
        raise ValueError(
            "moment_counters needs moments from ensemble_moments "
            "(constancy masks)"
        )
    where = np.nonzero(moments.horizons == reference_horizon)[0]
    if where.size == 0:
        raise ValueError(
            f"reference horizon {reference_horizon} is not among the horizons"
        )
    cp, plp = moments.cp_constant, moments.plp_constant
    return {
        "zero_variance_corr": int((cp | plp).sum()),
        "zero_variance_corr_cp": int(cp.sum()),
        "zero_variance_corr_plp": int(plp.sum()),
        "curvature_floor": int((curvature(moments) < 1e-300).sum()),
        "decisive_floor": int((moments.sq_plp[:, where[0]] < 1e-300).sum()),
    }


# ---------------------------------------------------------------------- fitting
def fit_rules(cells: list[Cell], config: StudyConfig) -> FittedRules:
    """Fit A2, A3, the seed proxies and the regime maps on core cells (pooled).

    The rules are the ways of choosing the blending weight ``w``: a single
    global weight (A2), a neural error predictor (A3), and a small decision
    tree that sorts states into regimes with one weight each (A5). All are
    fitted on the construction split and tuned on the calibration split.

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
        np.concatenate([s.moments.est_seed for s in con]),
        noise,
    )

    con_moments = _concat_moments([s.moments for s in con])
    cal_moments = _concat_moments([s.moments for s in cal])
    a2 = global_weight(con_moments)
    predictor = ErrorPredictor.fit(
        con_moments.kept["inputs"],
        con_moments.kept["cp_err"],
        con_moments.kept["plp_err"],
        allocator_grid(config),
        noise,
        width=64,
        epochs=config.allocator_epochs,
        rng=make_rng(
            config.seed, cells[0].system, cells[0].ctx.embed_dim, "allocator"
        ),
    )

    con_profile = np.concatenate(
        [
            deployable_profile(
                s.evals, proxies, noise, config.steps_per_lyapunov
            )
            for s in con
        ]
    )
    cal_profile = np.concatenate(
        [
            deployable_profile(
                s.evals, proxies, noise, config.steps_per_lyapunov
            )
            for s in cal
        ]
    )
    cal_evals = _concat_evals([s.evals for s in cal])
    w_target = oracle_weight(con_moments)[:, href_col]
    t_target = np.log(
        state_horizon_target(con_moments, noise, config.primary_threshold)
    )
    regimes, chosen = fit_regime_maps(
        con_profile,
        cal_profile,
        w_target,
        t_target,
        cal_moments,
        cal_evals,
        a2,
        config,
    )
    return FittedRules(
        proxies=proxies,
        global_weights=a2,
        predictor=predictor,
        regimes=regimes,
        chosen_regimes=chosen,
        handled=fit_counters(
            regimes,
            chosen,
            pooled_floor_count(con_moments),
            constant_target_count(w_target, t_target),
        ),
    )


def fit_regime_maps(
    con_profile: np.ndarray,
    cal_profile: np.ndarray,
    w_target: np.ndarray,
    t_target: np.ndarray,
    cal_moments: EnsembleMoments,
    cal_evals: EvaluationDraws,
    fallback: np.ndarray,
    config: StudyConfig,
) -> tuple[dict[int, RegimeMap], int]:
    """Fit and calibrate the A5 regime maps for every ``K``, and choose ``K``.

    One tree per ``K`` of ``config.regime_counts`` is fitted on the
    construction profiles (:func:`fit_regime_tree`), its leaf weights are set
    on calibration (:func:`calibrate_regimes`) and ``K`` is chosen by the v3
    rule (:func:`_choose_regimes`). :func:`fit_rules` calls it with the four
    deployable coordinates; ablation (b3) of WU-0039b calls it with three.

    Parameters
    ----------
    con_profile, cal_profile : np.ndarray
        Deployable profiles of the construction and calibration splits,
        shape ``(n, E, p)``.
    w_target, t_target : np.ndarray
        Tree targets per construction state: ``w*(H_ref)`` and the log
        characteristic horizon.
    cal_moments : EnsembleMoments
        Calibration oracle moments.
    cal_evals : EvaluationDraws
        Calibration evaluation draws.
    fallback : np.ndarray
        Weights of an empty regime (A2), shape ``(nH,)``.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    tuple[dict[int, RegimeMap], int]
        The calibrated maps by ``K`` and the chosen ``K``.
    """
    regimes: dict[int, RegimeMap] = {}
    for n_reg in config.regime_counts:
        tree = fit_regime_tree(
            con_profile, w_target, t_target, n_reg, config.seed
        )
        regimes[n_reg] = calibrate_regimes(
            tree,
            cal_profile,
            cal_moments,
            cal_evals,
            config.primary_threshold,
            fallback,
        )
    chosen = _choose_regimes(regimes, cal_profile, cal_moments, config)
    return regimes, chosen


FIT_COUNTERS: tuple[str, ...] = (
    "empty_regime_fallback",
    "empty_regime_fallback_chosen",
    "pooled_curvature_floor",
    "regime_target_constant",
)
"""Scalar counters of one ``fit_rules`` call.

``empty_regime_fallback_by_K`` (a dict keyed by the string of ``K``) comes with
them in ``FittedRules.handled``."""


def fit_counters(
    regimes: dict[int, RegimeMap],
    chosen: int,
    a2_floor: int,
    target_constant: int,
) -> dict[str, object]:
    """Count the special cases of one rule fit (DEF-0001).

    Q4 of DEC-0017 renames the ROADMAP key.

    * ``empty_regime_fallback``: (K, regime) pairs with no calibration (state,
      draw), summed over all fitted ``K``, with ``empty_regime_fallback_by_K``
      and the count at the chosen ``K`` (``empty_regime_fallback_chosen``: only
      the chosen ``K`` reaches A5 and H3).
    * ``pooled_curvature_floor``: the A2 pool plus every regime pool of every
      ``K`` whose summed curvature was below ``1e-300`` at some horizon (summed
      over horizons).
    * ``regime_target_constant``: constant tree targets, once per fit (D7).

    Parameters
    ----------
    regimes : dict[int, RegimeMap]
        Calibrated maps by ``K`` (built by ``calibrate_regimes``).
    chosen : int
        The chosen ``K``.
    a2_floor : int
        :func:`pooled_floor_count` of the A2 pool.
    target_constant : int
        :func:`constant_target_count` of the tree targets.

    Returns
    -------
    dict[str, object]
        The counters of ``FIT_COUNTERS`` and ``empty_regime_fallback_by_K``.
    """
    by_k = {str(k): int(regimes[k].empty.sum()) for k in sorted(regimes)}
    return {
        "empty_regime_fallback": sum(by_k.values()),
        "empty_regime_fallback_by_K": by_k,
        "empty_regime_fallback_chosen": by_k[str(chosen)],
        "pooled_curvature_floor": int(
            a2_floor + sum(r.pooled_curvature_floor for r in regimes.values())
        ),
        "regime_target_constant": int(target_constant),
    }


# ------------------------------------------------- the handling block
HANDLING_SCHEMA: str = "lpcstudy.handling/2"
"""Schema id of the handling block.

``/2`` (WU-0005.4) adds the ``lm`` block of each cell and the counters
``lm_nonfinite_cost`` and ``lm_nonfinite_jacobian``; nothing of ``/1`` is
removed or changed."""

CELL_COUNTERS: tuple[str, ...] = (
    "invariant_mean_replacements",
    "nu_replacements",
    "error_clips",
    "error_clips_cp",
    "error_clips_plp",
    "error_clips_nonfinite",
    "error_clips_plp_href",
    "error_clips_nonfinite_href",
    "gain_replacements",
    "gain_floor",
    "zero_variance_corr",
    "zero_variance_corr_cp",
    "zero_variance_corr_plp",
    "curvature_floor",
    "decisive_floor",
    "lm_nonfinite_cost",
    "lm_nonfinite_jacobian",
)
"""Counters of a cell record (per kind and in total).

They are ``DRAW_COUNTERS`` and ``ENTRY_COUNTERS`` (from ``ensemble``), their
sum ``error_clips``, and ``moment_counters``."""

EVALUATION_COUNTERS: tuple[str, ...] = (
    "nu_cap_clips",
    "closed_form_floor_a4",
    "closed_form_floor_a4o",
)
"""Proxy-dependent counters of the ``evaluation`` block of a core cell."""

ALL_COUNTERS: tuple[str, ...] = (
    *CELL_COUNTERS,
    *ORACLE_COUNTERS,
    *EVALUATION_COUNTERS,
    *FIT_COUNTERS,
)
"""Every counter name; the ``totals`` of a block carry exactly these keys."""

KINDS: tuple[str, ...] = ("oracle", "eval", "check")
"""Where the counts of a cell record come from.

They come from oracle draws, evaluation draws, or a validation check (V3, V4)
that draws its own forecasts."""

CELL_DENOMINATORS: tuple[str, ...] = (
    "estimates",
    "error_entries",
    "href_draws",
    "eval_draws",
    "moment_entries",
    "states",
)

COUNTER_DENOMINATOR: dict[str, str | None] = {
    "invariant_mean_replacements": "estimates",
    "nu_replacements": "estimates",
    "error_clips": None,
    "error_clips_cp": "error_entries",
    "error_clips_plp": "error_entries",
    "error_clips_nonfinite": "error_entries",
    "error_clips_plp_href": "href_draws",
    "error_clips_nonfinite_href": "href_draws",
    "gain_replacements": "eval_draws",
    "gain_floor": "eval_draws",
    "zero_variance_corr": "moment_entries",
    "zero_variance_corr_cp": "moment_entries",
    "zero_variance_corr_plp": "moment_entries",
    "curvature_floor": "moment_entries",
    "decisive_floor": "states",
    "lm_nonfinite_cost": "estimates",
    "lm_nonfinite_jacobian": "estimates",
    "local_dim_zero_distance": "states",
    "oracle_gain_floor": "states",
    "oracle_nonfinite": "states",
    "nu_cap_clips": "nu_cap_estimates",
    "closed_form_floor_a4": "test_eval_draws",
    "closed_form_floor_a4o": "test_states",
    "empty_regime_fallback": "regimes",
    "empty_regime_fallback_chosen": "chosen_regimes",
    "pooled_curvature_floor": "pools",
    "regime_target_constant": "targets",
}
"""The denominator of each counter (a key of ``denominators`` of the block).

``None`` marks a total that mixes CP and PLP entries, so it has no
denominator."""


def cell_id(label: str, noise: float, library_size: int, core: bool) -> str:
    """Return the id of a cell in ``handling.cells``.

    The form is ``<label>|rho=<g>|n_lib=<n>|core`` (or ``sweep``).
    """
    kind = "core" if core else "sweep"
    return f"{label}|rho={noise:g}|n_lib={library_size}|{kind}"


def _new_kind() -> dict:
    """Return an empty record (all counts and denominators zero) of one kind."""
    return {
        "counts": dict.fromkeys(CELL_COUNTERS, 0),
        "denominators": dict.fromkeys(CELL_DENOMINATORS, 0),
    }


def _add_to_kind(
    kind: dict,
    handled: np.ndarray,
    clip_entries: dict[str, int],
    moment: dict[str, int] | None,
    denominators: dict[str, int],
) -> None:
    """Add per-state columns, entry totals and moment counters to a kind."""
    counts = kind["counts"]
    for name in DRAW_COUNTERS:
        counts[name] += int(handled[:, DRAW_COLUMN[name]].sum())
    for name in ENTRY_COUNTERS:
        counts[name] += int(clip_entries[name])
        counts["error_clips"] += int(clip_entries[name])
    for name, value in (moment or {}).items():
        counts[name] += int(value)
    for name, value in denominators.items():
        kind["denominators"][name] += int(value)


LMParts = dict[str, list[tuple[np.ndarray, np.ndarray, np.ndarray]]]
"""Per kind, the ``(residual, accepted, late_progress)`` arrays of each
computation of the cell."""


def _lm_arrays(
    parts: list[tuple[np.ndarray, np.ndarray, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Flatten and join the arrays of several computations.

    If there are no computations, the arrays are empty.
    """
    if not parts:
        return (
            np.zeros(0),
            np.zeros(0, dtype=np.int32),
            np.zeros(0, dtype=np.int32),
        )
    return tuple(
        np.concatenate([part[i].ravel() for part in parts]) for i in range(3)
    )


def lm_block(parts: LMParts, noise: float, dof: int) -> dict:
    """Return the ``lm`` block of a cell record.

    The block summarizes the Levenberg-Marquardt fits (the iterative search
    that estimates each starting state from noisy data); NVVUQ.10, WU-0005.4.

    Parameters
    ----------
    parts : dict
        ``KINDS`` name to the list of ``(residual, accepted, late_progress)``
        arrays of each computation of that kind (a missing kind has none).
    noise : float
        Noise level ``rho`` of the cell.
    dof : int
        Degrees of freedom ``D - m`` of the goodness-of-fit reference (stored
        as ``gof_dof``): ``embed_dim - state dimension``, 4 for the main
        systems.

    Returns
    -------
    dict
        ``lm_summary`` of all estimates of the cell, plus ``by_kind``: the
        summary of each kind of ``KINDS`` (``n_estimates`` 0 and ``None``
        values for a kind without estimates). It is not summed into ``totals``
        (``sum_totals`` reads ``counts`` only). Report-only: no verdict reads
        it. Needs owner review before freeze.
    """
    by_kind = {
        kind: lm_summary(*_lm_arrays(parts.get(kind, [])), noise, dof)
        for kind in KINDS
    }
    pooled = [part for kind in KINDS for part in parts.get(kind, [])]
    return {**lm_summary(*_lm_arrays(pooled), noise, dof), "by_kind": by_kind}


def cell_record(kinds: dict[str, dict], lm: dict | None = None) -> dict:
    """Assemble a cell record from its kinds (missing kinds are zero).

    Counts and denominators are the sums over ``KINDS``; ``by_kind`` keeps the
    parts. ``lm`` is the ``lm_block`` (added under the key ``lm`` when given).
    """
    full = {kind: kinds.get(kind) or _new_kind() for kind in KINDS}
    record = {
        "counts": {
            name: sum(full[k]["counts"][name] for k in KINDS)
            for name in CELL_COUNTERS
        },
        "by_kind": full,
        "denominators": {
            name: sum(full[k]["denominators"][name] for k in KINDS)
            for name in CELL_DENOMINATORS
        },
    }
    if lm is not None:
        record["lm"] = lm
    return record


def _lm_part(
    source: EnsembleMoments | EvaluationDraws, name: str, shape: tuple[int, int]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the Levenberg-Marquardt arrays of a computation, shape checked."""
    arrays = tuple(getattr(source, field_name) for field_name in LM_FIELDS)
    if any(a is None for a in arrays):
        raise ValueError(
            f"{name}: carries no Levenberg-Marquardt arrays "
            "(built by hand or a view)"
        )
    if any(a.shape != shape for a in arrays):
        raise ValueError(
            f"{name}: Levenberg-Marquardt arrays have shapes "
            f"{[a.shape for a in arrays]}, expected {shape} each"
        )
    return arrays


def cell_handling(
    splits: dict[str, SplitData],
    n_oracle_draws: int,
    reference_horizon: int,
    noise: float,
    dof: int,
) -> dict:
    """Return the handling record of one cell, from the counts it stored.

    The record sums over the splits: the oracle kind from the moments
    (per-state ``handled``, the entry totals, and the moment-derived counters),
    and the eval kind from the evaluation draws. Nothing is recomputed and
    nothing is drawn.

    Parameters
    ----------
    splits : dict[str, SplitData]
        The splits of the cell as made by ``Study.run_cell``.
    n_oracle_draws : int
        Oracle draws per state ``M`` (the moments do not store it).
    reference_horizon : int
        ``H_ref`` in steps.
    noise : float
        Noise level ``rho`` of the cell (scales the goodness-of-fit reading of
        the ``lm`` block).
    dof : int
        ``D - m`` of the cell (embedding dimension minus state dimension), the
        degrees of freedom of the chi-square reference of ``c / rho^2``.

    Returns
    -------
    dict
        ``{counts, by_kind, denominators, lm}`` with every counter of
        ``CELL_COUNTERS`` and every denominator of ``CELL_DENOMINATORS``
        present, and the ``lm_block`` of the cell.

    Raises
    ------
    ValueError
        If the moments or draws of a split carry no counts or no
        Levenberg-Marquardt arrays (built by hand, or after a subset), or the
        arrays do not have the shape of the draws.
    """
    oracle, evaluation = _new_kind(), _new_kind()
    lm_parts: LMParts = {"oracle": [], "eval": []}
    for name, data in splits.items():
        moments, evals = data.moments, data.evals
        if moments.handled is None or moments.clip_entries is None:
            raise ValueError(
                f"split {name!r}: moments carry no counts "
                "(built by hand or a view)"
            )
        n, n_hor = len(moments.handled), len(moments.horizons)
        lm_parts["oracle"].append(
            _lm_part(moments, f"split {name!r} moments", (n, n_oracle_draws))
        )
        _add_to_kind(
            oracle,
            moments.handled,
            moments.clip_entries,
            moment_counters(moments, reference_horizon),
            {
                "states": n,
                "estimates": n * n_oracle_draws,
                "error_entries": n * n_oracle_draws * n_hor,
                "href_draws": n * n_oracle_draws,
                "moment_entries": n * n_hor,
            },
        )
        if evals is not None:
            if evals.handled is None or evals.clip_entries is None:
                raise ValueError(
                    f"split {name!r}: evaluation draws carry no counts"
                )
            draws, n_hor_ev = evals.cp_err.shape[1], evals.cp_err.shape[2]
            lm_parts["eval"].append(
                _lm_part(evals, f"split {name!r} evaluation draws", (n, draws))
            )
            _add_to_kind(
                evaluation,
                evals.handled,
                evals.clip_entries,
                None,
                {
                    "estimates": n * draws,
                    "error_entries": n * draws * n_hor_ev,
                    "href_draws": n * draws,
                    "eval_draws": n * draws,
                },
            )
    return cell_record(
        {"oracle": oracle, "eval": evaluation}, lm_block(lm_parts, noise, dof)
    )


def check_record(
    handled: dict[str, int],
    clip_entries: dict[str, int],
    n_states: int,
    n_draws: int,
    n_horizons: int,
    noise: float,
    dof: int,
    lm: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> dict:
    """Return the handling record of a validation check (V3, V4).

    These checks draw their own forecasts, so they are not cells.

    Parameters
    ----------
    handled : dict[str, int]
        Column sums of ``DrawBatch.handled`` by ``DRAW_COUNTERS`` name.
    clip_entries : dict[str, int]
        ``ENTRY_COUNTERS`` totals.
    n_states, n_draws, n_horizons : int
        Size of the check: states, draws per state, horizons.
    noise : float
        Noise level ``rho`` of the check.
    dof : int
        ``D - m`` of the system of the check (see ``cell_handling``).
    lm : tuple of np.ndarray
        ``(residual, accepted, late_progress)`` of the estimates of the check,
        ``n_states * n_draws`` values each. They are summarized here and not
        stored.

    Returns
    -------
    dict
        A cell record with only the ``check`` kind filled (``lm`` block
        included).

    Raises
    ------
    ValueError
        If the arrays do not hold ``n_states * n_draws`` values.
    """
    if any(np.size(a) != n_states * n_draws for a in lm):
        raise ValueError(
            f"check_record: expected {n_states * n_draws} estimates per array, "
            f"got {[np.size(a) for a in lm]}"
        )
    kind = _new_kind()
    matrix = np.array(
        [[handled[name] for name in DRAW_COUNTERS]], dtype=np.int64
    )
    _add_to_kind(
        kind,
        matrix,
        clip_entries,
        None,
        {
            "states": n_states,
            "estimates": n_states * n_draws,
            "error_entries": n_states * n_draws * n_horizons,
            "href_draws": n_states * n_draws,
        },
    )
    return cell_record({"check": kind}, lm_block({"check": [lm]}, noise, dof))


def oracle_block(oracles: StateOracles) -> dict:
    """Return the counts of one split's state oracles.

    The form is ``{counts: ORACLE_COUNTERS, denominators: {states}}``.
    """
    if oracles.handled is None:
        raise ValueError(
            "the state oracles carry no counts (built by hand or a view)"
        )
    return {
        "counts": {
            name: int(oracles.handled[:, i].sum())
            for i, name in enumerate(ORACLE_COUNTERS)
        },
        "denominators": {"states": int(len(oracles.handled))},
    }


def evaluation_block(cell: Cell, rules: FittedRules) -> dict:
    """Return the proxy-dependent counters of a core cell after ``fit_rules``.

    These are the counters D3 and D6.

    * ``nu_cap_clips``: estimates ``nu_hat > nu_cap`` of the fitted proxies,
      per split and in total. On construction about 1% by construction of the
      99th-percentile cap; on the other splits a diagnostic.
    * ``closed_form_floor_a4``: test-split evaluation draws on which the floor
      of the A4 weight binds (``eps_hat^2 + delta_hat^2 < 1e-300``);
      ``closed_form_floor_a4o``: test states with oracle seeds on which it
      binds (A4o). Both are sentinels.

    Counted from arrays; nothing inside ``ProfileProxies.features`` (it runs
    many times).
    """
    cap = rules.proxies.nu_cap
    by_split = {
        name: nu_cap_clip_count(data.evals.est_nu, cap)
        for name, data in cell.splits.items()
        if data.evals is not None
    }
    test = cell.splits["test"]
    eps_hat, delta_hat = rules.proxies.seeds(test.evals, cell.noise)
    moments = test.moments
    return {
        "counts": {
            "nu_cap_clips": sum(by_split.values()),
            "closed_form_floor_a4": closed_form_floor_count(
                eps_hat**2, delta_hat**2
            ),
            "closed_form_floor_a4o": closed_form_floor_count(
                moments.analog_seed**2, moments.est_seed**2
            ),
        },
        "by_split": {"nu_cap_clips": by_split},
        "denominators": {
            "nu_cap_estimates": int(
                sum(
                    data.evals.est_nu.size
                    for data in cell.splits.values()
                    if data.evals is not None
                )
            ),
            "test_eval_draws": int(test.evals.est_nu.size),
            "test_states": int(len(moments.analog_seed)),
        },
    }


def fit_block(rules: FittedRules, n_horizons: int) -> dict:
    """Return the ``fitting`` block of rules fitted on a core cell.

    ``n_horizons`` is the number of horizons of the cell.
    """
    counts = {name: int(rules.handled[name]) for name in FIT_COUNTERS}
    n_regimes = sum(rules.regimes)
    return {
        "counts": counts,
        "empty_regime_fallback_by_K": dict(
            rules.handled["empty_regime_fallback_by_K"]
        ),
        "denominators": {
            "regimes": int(n_regimes),
            "chosen_regimes": int(rules.chosen_regimes),
            "pools": int(n_horizons * (1 + n_regimes)),
            "targets": 2,
        },
    }


def empty_fit_block() -> dict:
    """Return a ``fitting`` block of zeros, for a system never fitted."""
    return {
        "counts": dict.fromkeys(FIT_COUNTERS, 0),
        "empty_regime_fallback_by_K": {},
        "denominators": {
            "regimes": 0,
            "chosen_regimes": 0,
            "pools": 0,
            "targets": 0,
        },
    }


def sum_totals(blocks: list[dict]) -> dict[str, int]:
    """Sum every counter of ``ALL_COUNTERS`` over blocks.

    Each block contributes its ``counts``, and, if present, those of its
    ``evaluation`` and ``fitting`` sub-blocks. A counter no block carries is 0,
    so every key is present.
    """
    totals = dict.fromkeys(ALL_COUNTERS, 0)
    for block in blocks:
        for part in (block, block.get("evaluation"), block.get("fitting")):
            for name, value in (part or {}).get("counts", {}).items():
                totals[name] += int(value)
    return totals


def choose_regime_count(
    excess_by_count: Mapping[int, float], margin: float = 0.05
) -> int:
    """Choose the smallest ``K`` that is within ``margin`` of the best (M2 §M7).

    ``K`` is the number of regimes. A larger ``K`` always fits calibration
    data a little better, so we take the smallest ``K`` whose calibration
    excess mean squared error is close enough to the minimum.

    The rule is ``excess_K <= (1.0 + margin) * min_K excess_K`` on the
    unrounded float64 values, ``K`` taken in increasing order; a tie at the
    edge counts as inside. A "tie" is defined on this expression with
    ``min = 1.0`` (``1.0 + 0.05 == 1.05`` in float64), not on
    ``excess - min <= margin * min``, which judges 1.05 against 1.0 as outside
    (DEC-0008 A1, A5). The quantity is the absolute calibration excess
    ``V(w_K) - V(w*)`` (Theorem P1(a)), not the ratio to the best single
    forecaster.

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
        If the mapping is empty, ``margin`` is negative, or a value is not
        finite or is negative (the exact excess is non-negative, so a negative
        value is a bug and would invert the margin).
    """
    if margin < 0.0:
        raise ValueError(f"margin must be >= 0, got {margin}")
    if not excess_by_count:
        raise ValueError("choose_regime_count needs at least one candidate K")
    values = {k: float(excess_by_count[k]) for k in sorted(excess_by_count)}
    for count, value in values.items():
        if not np.isfinite(value) or value < 0.0:
            raise ValueError(
                f"excess MSE for K={count} must be finite and >= 0, got {value}"
            )
    minimum = min(values.values())
    return next(
        count
        for count, value in values.items()
        if value <= (1.0 + margin) * minimum
    )


def _choose_regimes(
    regimes: dict[int, RegimeMap],
    profile: np.ndarray,
    moments: EnsembleMoments,
    config: StudyConfig,
) -> int:
    """Choose ``K`` by the §M7 rule on the calibration excess MSE at ``H_ref``.

    This is DEC-0008 A5. The candidates are the ``K`` of ``regimes`` up to
    ``config.regime_max_primary``; the horizon column is located by value
    (``horizons == reference_horizon``).
    """
    column = int(np.nonzero(moments.horizons == config.reference_horizon)[0][0])
    excess = {
        k: regime_regret(regimes[k], profile, moments, column)[0]
        for k in sorted(regimes)
        if k <= config.regime_max_primary
    }
    return choose_regime_count(excess)


def _concat_moments(parts: list[EnsembleMoments]) -> EnsembleMoments:
    """Stack the moments of several cells (same horizons)."""
    if len(parts) == 1:
        return parts[0]
    keys = (
        "mean_cp",
        "mean_plp",
        "sq_cp",
        "sq_plp",
        "cross",
        "analog_seed",
        "est_seed",
        "noise_sens",
    )
    kept_keys = set.intersection(*(set(p.kept) for p in parts))
    correlation = {}
    for key in CORRELATION_FIELDS:  # all parts carry the field, or none does
        present = [getattr(p, key) is not None for p in parts]
        if any(present) and not all(present):
            raise ValueError(f"cannot stack moments: only some carry {key!r}")
        correlation[key] = (
            np.concatenate([getattr(p, key) for p in parts])
            if all(present)
            else None
        )
    return EnsembleMoments(
        horizons=parts[0].horizons,
        kept={k: np.concatenate([p.kept[k] for p in parts]) for k in kept_keys},
        handled=_stack_handled(parts),
        clip_entries=_sum_entries(parts),
        clip_cross_ref=stack_optional([p.clip_cross_ref for p in parts]),
        **{
            k: stack_optional([getattr(p, k) for p in parts]) for k in LM_FIELDS
        },
        **correlation,
        **{k: np.concatenate([getattr(p, k) for p in parts]) for k in keys},
    )


def _concat_evals(parts: list[EvaluationDraws]) -> EvaluationDraws:
    """Stack the evaluation draws of several cells (same horizons)."""
    if len(parts) == 1:
        return parts[0]
    stacked = {
        k: np.concatenate([getattr(p, k) for p in parts])
        for k in parts[0].__dict__
        if k
        not in (
            "horizons",
            "handled",
            "clip_entries",
            "clip_sign_ref",
            *LM_FIELDS,
        )
    }
    return EvaluationDraws(
        horizons=parts[0].horizons,
        handled=_stack_handled(parts),
        clip_entries=_sum_entries(parts),
        clip_sign_ref=stack_optional([p.clip_sign_ref for p in parts]),
        **{
            k: stack_optional([getattr(p, k) for p in parts]) for k in LM_FIELDS
        },
        **stacked,
    )


def _stack_handled(parts: list) -> np.ndarray | None:
    """Stack the per-state ``handled`` arrays of several cells.

    Returns ``None`` if none of them carries one.
    """
    present = [p.handled is not None for p in parts]
    if any(present) and not all(present):
        raise ValueError("cannot stack: only some parts carry 'handled'")
    return np.concatenate([p.handled for p in parts]) if all(present) else None


def _sum_entries(parts: list) -> dict[str, int] | None:
    """Add the ``clip_entries`` totals of several cells.

    Returns ``None`` if any part lacks them.
    """
    if any(p.clip_entries is None for p in parts):
        return None
    return {
        k: sum(p.clip_entries[k] for p in parts) for k in parts[0].clip_entries
    }


# ------------------------------------------------------------------- evaluation
def rule_weights(
    rules: FittedRules,
    split: SplitData,
    noise: float,
    config: StudyConfig,
    horizons: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return the weights of every rule on one split's evaluation draws.

    A weight of 1 means "trust CP only" and 0 means "trust PLP only". The
    rules are A0 (always CP), A1 (always PLP), A2 (one global weight), A3
    (error predictor), A4 (closed form from estimated seeds), A5 (regimes),
    A4o (closed form from oracle seeds) and A* (the oracle best weight).

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
        Horizons of the arrays of the split.

    Returns
    -------
    dict[str, np.ndarray]
        Rule label to weights ``(n, E, nH)``.
    """
    ev = split.evals
    shape = ev.cp_err.shape
    eps_hat, delta_hat = rules.proxies.seeds(ev, noise)
    profile = deployable_profile(
        ev, rules.proxies, noise, config.steps_per_lyapunov
    )
    regime_map = rules.regimes[rules.chosen_regimes]
    regime = regime_map.assign(profile)
    moments = split.moments
    oracle_cf = closed_form_weight(moments.analog_seed**2, moments.est_seed**2)
    return {
        "A0": np.ones(shape),
        "A1": np.zeros(shape),
        "A2": np.broadcast_to(rules.global_weights[horizons - 1], shape).copy(),
        "A3": rules.predictor.weights(ev.inputs, horizons),
        "A4": np.broadcast_to(
            closed_form_weight(eps_hat**2, delta_hat**2)[..., None], shape
        ).copy(),
        "A5": regime_map.weights[regime][..., horizons - 1],
        "A4o": np.broadcast_to(oracle_cf[:, None, None], shape).copy(),
        "A*": np.broadcast_to(oracle_weight(moments)[:, None, :], shape).copy(),
    }


@dataclass
class RuleScores:
    """The scores of one rule on one split.

    Attributes
    ----------
    mse : np.ndarray
        Realized mean squared error per horizon ``(nH,)`` (noise-free truth).
    state_mse_ref : np.ndarray
        Per-state realized squared error at ``H_ref`` averaged over draws
        ``(n,)``.
    regret : np.ndarray
        Mean exact excess error ``V(w) - V(w*)`` per horizon ``(nH,)``
        (Theorem P1(a)).
    agreement : float
        Fraction of decisive states at ``H_ref`` where the rule weights the
        better forecaster more (NaN when no state is decisive: visible, not
        replaced; DEF-0001, J).
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


def score_rules(
    weights: dict[str, np.ndarray],
    split: SplitData,
    horizons: np.ndarray,
    config: StudyConfig,
    theta: float,
) -> dict[str, RuleScores]:
    """Score every rule on a split.

    For each rule the blended error is ``w * e_CP + (1 - w) * e_PLP``. The
    scores are its mean squared error, its regret (excess over the best
    possible weight), its agreement with the better forecaster, and the
    Kaplan-Meier summary of its realized horizons.

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
    decisive_ratio = np.sqrt(
        moments.sq_cp[:, ref] / np.maximum(moments.sq_plp[:, ref], 1e-300)
    )
    decisive = np.abs(np.log(decisive_ratio)) >= np.log(1.1)
    cp_better = decisive_ratio < 1.0
    contiguous = np.array_equal(horizons, np.arange(1, len(horizons) + 1))
    lt = config.steps_per_lyapunov
    scores: dict[str, RuleScores] = {}
    for name, w in weights.items():
        err = w * ev.cp_err + (1 - w) * ev.plp_err
        sq = err**2
        regret = np.mean(excess_mse(moments, w), axis=(0, 1))
        favors_cp = w[:, :, ref].mean(axis=1) > 0.5
        agreement = (
            float(np.mean(favors_cp[decisive] == cp_better[decisive]))
            if decisive.any()
            else float("nan")
        )
        km_median = rmst = float("nan")
        durations = events = np.empty(0)
        if contiguous:
            durations, events = realized_horizon(
                err - ev.verify_noise, horizons, theta
            )
            curve = kaplan_meier(durations, events, len(horizons))
            km_median, rmst = curve.median() / lt, curve.restricted_mean() / lt
        scores[name] = RuleScores(
            mse=sq.mean(axis=(0, 1)),
            state_mse_ref=sq[:, :, ref].mean(axis=1),
            regret=regret,
            agreement=agreement,
            km_median=km_median,
            rmst=rmst,
            durations=durations,
            events=events,
        )
    return scores
