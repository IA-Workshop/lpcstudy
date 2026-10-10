"""Experiment orchestration: stages (i)-(v) of the proposal.

Stage (i)   dynamical-system generation        -> ``Study.context``
Stage (ii)  mechanism validation               -> :func:`run_system` (V1-V6, E1, E2)
Stage (iii) allocation and horizon testing     -> :func:`run_system` (E3, E4)
Stage (iv)  state abstraction and benchmarking -> :func:`run_system` (E5)
Stage (v)   robustness and transfer            -> :func:`run_robustness`, :func:`run_transfer`
"""

from __future__ import annotations

import logging
import time

import jax.numpy as jnp
import numpy as np

from . import analysis as an
from .allocation import deployable_profile, regime_regret
from .config import StudyConfig
from .dynamics import make_finite_growth
from .ensemble import AnalogLibrary, forecast_draws
from .oracle import oracle_weight
from .pipeline import Cell, FittedRules, Study, fit_rules, rule_weights, score_rules
from .statistics import block_bootstrap, partial_correlation
from .validation import check_cp_horizon, check_cramer_rao, check_integrator, \
    check_jacobians, check_kaplan_meier, gate_status

LOG = logging.getLogger("lpcstudy")


def _sweep_subset(cell: Cell, config: StudyConfig) -> Cell:
    """Core cell restricted to the test-sweep states and the evaluation horizons."""
    from .pipeline import SplitData

    rows = np.arange(config.n_test_sweep)
    cols = np.array(config.eval_horizons) - 1
    test = cell.splits["test"]
    m = test.moments.subset(rows)
    for attr in ("mean_cp", "mean_plp", "sq_cp", "sq_plp", "cross"):
        setattr(m, attr, getattr(m, attr)[:, cols])
    m.horizons = np.array(config.eval_horizons)
    ev = test.evals.subset(rows)
    for attr in ("cp_err", "plp_err", "verify_noise", "gain_proxy"):
        setattr(ev, attr, getattr(ev, attr)[:, :, cols])
    ev.horizons = np.array(config.eval_horizons)
    return Cell(system=cell.system, noise=cell.noise, library_size=cell.library_size,
                label=cell.label, setup=cell.setup, splits={"test": SplitData(m, ev)},
                oracles={"test": cell.oracles["test"].subset(rows)},
                horizons=np.array(config.eval_horizons))


def convergence_check(study: Study, cell: Cell) -> dict:
    """V4: bootstrap half-width of ``w*(H_ref)`` as a function of ``M``.

    Parameters
    ----------
    study : Study
        Study (configuration and noise generators).
    cell : Cell
        Core cell.

    Returns
    -------
    dict
        Median half-width and mean deviation from the largest-``M`` estimate.
    """
    cfg = study.config
    ctx = cell.ctx
    n = min(cfg.convergence_states, cfg.n_test)
    noise = study.unit_noise(ctx, "test", "convergence", max(cfg.convergence_draws),
                             ctx.embed_dim)[:n]
    library = AnalogLibrary.build(ctx, cell.noise, cell.library_size, cfg.horizon_max)
    horizons = np.array([cfg.reference_horizon])
    cp, plp = [], []
    for start in range(0, n, 5):
        rows = np.arange(start, min(n, start + 5))
        batch = forecast_draws(cell.setup, library, "test", rows, noise[rows], horizons)
        cp.append(batch.cp_err[:, :, 0])
        plp.append(batch.plp_err[:, :, 0])
    cp, plp = np.concatenate(cp), np.concatenate(plp)

    def weight(c: np.ndarray, p: np.ndarray) -> np.ndarray:
        num = np.mean(p * (p - c), axis=-1)
        den = np.mean((c - p) ** 2, axis=-1)
        return np.clip(num / np.maximum(den, 1e-300), 0, 1)

    rng = np.random.default_rng(cfg.seed)
    reference = weight(cp, plp)
    out = {}
    for m_draws in cfg.convergence_draws:
        base = weight(cp[:, :m_draws], plp[:, :m_draws])
        boots = np.stack([weight(cp[:, idx], plp[:, idx]) for idx in
                          rng.integers(0, m_draws, (200, m_draws))])
        half = 0.5 * (np.percentile(boots, 97.5, axis=0) - np.percentile(boots, 2.5, axis=0))
        out[str(m_draws)] = {"median_half_width": float(np.median(half)),
                             "mean_abs_dev_from_max": float(np.mean(np.abs(base - reference)))}
    used = out.get(str(cfg.n_oracle_draws))
    out["used_M"] = cfg.n_oracle_draws
    out["pass"] = bool(used is not None and used["median_half_width"] <= 0.05)
    return out


def _evaluate(cell: Cell, rules: FittedRules, config: StudyConfig, split: str = "test"):
    """Rule weights and scores on one split of a cell."""
    data = cell.splits[split]
    weights = rule_weights(rules, data, cell.noise, config, cell.horizons)
    return weights, score_rules(weights, data, cell.horizons, config,
                                config.primary_threshold)


def run_system(study: Study, system: str) -> dict:
    """Stages (ii)-(iv) for one core system.

    Parameters
    ----------
    study : Study
        Study object.
    system : str
        System name.

    Returns
    -------
    dict
        JSON-serializable results; also stores the core cell and fitted rules in
        ``study`` for transfer.
    """
    cfg = study.config
    t0 = time.time()
    ctx = study.context(system)
    res: dict = {"context": ctx.meta}

    # Core cell and validation gate.
    core = study.run_cell(system, cfg.core_noise, cfg.core_library, core=True,
                          with_evals=True)
    library = AnalogLibrary.build(ctx, cfg.core_noise, cfg.core_library, cfg.horizon_max)
    vt = study.unit_noise(ctx, "test", "eval", 1, ctx.embed_dim)
    vv = study.unit_noise(ctx, "test", "verify", 1, cfg.horizon_max)
    res["validation"] = {
        **check_jacobians(ctx), **check_cramer_rao(ctx), **check_kaplan_meier(),
        **check_integrator(ctx),
        **check_cp_horizon(core.setup, library, vt, vv, cfg.horizon_max, 0.4,
                           cfg.steps_per_lyapunov),
        "convergence": convergence_check(study, core),
        "estimators": {k: v for k, v in study.estimator_log.items() if system in k}}
    res["validation"]["gate"] = gate_status(res["validation"])
    if not res["validation"]["gate"]["gate_pass"]:
        LOG.warning("%s: VALIDATION GATE FAILED %s; results are flagged as provisional",
                    system, res["validation"]["gate"])
    LOG.info("%s validation: %s", system, res["validation"])

    rules = fit_rules([core], cfg)
    _, scores = _evaluate(core, rules, cfg)
    res["fitted"] = {"analog_proxy": vars(rules.proxies.analog),
                     "estimation_proxy": vars(rules.proxies.estimation),
                     "nu_cap": rules.proxies.nu_cap,
                     "chosen_K": rules.chosen_regimes,
                     "regime_weights_href": {
                         str(k): r.weights[:, cfg.reference_horizon - 1].tolist()
                         for k, r in rules.regimes.items()},
                     "regime_horizons_km_lyapunov": {
                         str(k): (r.horizons_km / cfg.steps_per_lyapunov).tolist()
                         for k, r in rules.regimes.items()}}
    res["scores"] = an.summarize_scores(scores, core.horizons, cfg)
    res["km_curves"] = an.km_curves(scores, cfg.horizon_max)
    res["weight_profile"] = an.weight_profiles(core, cfg)

    # Sweeps (common random numbers across levels).
    core_sub = _sweep_subset(core, cfg)
    noise_cells = {cfg.core_noise: core_sub}
    shift_scores = {}
    for rho in cfg.noise_levels:
        if rho != cfg.core_noise:
            noise_cells[rho] = study.run_cell(system, rho, cfg.core_library, core=False,
                                              with_evals=True)
            shift_scores[f"rho={rho:g}"] = _evaluate(noise_cells[rho], rules, cfg)[1]
    library_cells = {}
    extreme_sizes = (min(cfg.library_sizes), max(cfg.library_sizes))
    for rho in cfg.library_sweep_noises:
        for size in cfg.library_sizes:
            if rho == cfg.core_noise and size == cfg.core_library:
                library_cells[(rho, size)] = core_sub
                continue
            if size == cfg.core_library and rho in noise_cells:
                library_cells[(rho, size)] = noise_cells[rho]
                continue
            shifted = rho == cfg.core_noise and size in extreme_sizes
            library_cells[(rho, size)] = study.run_cell(system, rho, size, core=False,
                                                        with_evals=shifted)
            if shifted:
                shift_scores[f"N={size}"] = _evaluate(library_cells[(rho, size)], rules,
                                                      cfg)[1]
    core_sub_scores = _evaluate(core_sub, rules, cfg)[1]
    shift = an.shift_gaps(core_sub_scores, shift_scores, cfg)
    res["shift"] = shift

    # Hypotheses.
    res["H1a"] = an.h1a_noise_scaling(noise_cells, cfg)
    res["H1b"] = an.h1b_library_scaling(library_cells, cfg)
    res["H1c"] = an.h1c_seed_amplifier(core, cfg)
    res["H1d"] = an.h1d_horizon_law(core, cfg)
    res["H1e"] = an.h1e_proxies(core, rules, cfg)
    res["H1f"] = an.h1f_noise_redundancy(core, rules, cfg)
    res["H2a"] = an.h2a_separation(core, cfg)
    res["H2b"] = an.h2b_knob_response(noise_cells, library_cells, cfg)
    res["H2c"] = an.h2c_state_dependence(scores, cfg)
    res["H2d"] = an.h2d_empirical_comparison(scores, shift, cfg)
    res["H2e"] = an.h2e_horizon_bound(core, cfg)
    res.update(an.h3_regimes(core, rules, scores, cfg))
    res["oracle_recovery"] = an.oracle_recovery(scores, cfg)
    res["seconds"] = time.time() - t0
    study.core_cells[system] = core
    study.fitted[system] = rules
    LOG.info("%s finished in %.0fs", system, res["seconds"])
    return res


def run_transfer_target(study: Study, system: str) -> None:
    """Core cell and in-system fit for a transfer-only target (e.g. Lorenz-96)."""
    cfg = study.config
    core = study.run_cell(system, cfg.core_noise, cfg.core_library, core=True,
                          with_evals=True)
    study.core_cells[system] = core
    study.fitted[system] = fit_rules([core], cfg)


def run_transfer(study: Study) -> dict:
    """Stage (v): regimes and rules fitted on the sources, applied to targets unchanged.

    Parameters
    ----------
    study : Study
        Study holding core cells of sources and targets.

    Returns
    -------
    dict
        Excess-MSE ratios (refit vs transferred) and the pre-registered comparison.
    """
    cfg = study.config
    sources = [study.core_cells[s] for s in cfg.transfer_sources]
    pooled = fit_rules(sources, cfg)
    ref = cfg.reference_horizon - 1
    out: dict = {"sources": list(cfg.transfer_sources),
                 "pooled_chosen_K": pooled.chosen_regimes}
    for target in cfg.transfer_targets:
        cell = study.core_cells[target]
        _, refit = _evaluate(cell, study.fitted[target], cfg)
        _, moved = _evaluate(cell, pooled, cfg)
        ratio = lambda s: {k: float(s[k].mse[ref] / s["A*"].mse[ref])
                           for k in ("A2", "A3", "A4", "A5")}
        r_refit, r_moved = ratio(refit), ratio(moved)
        gap = {k: r_moved[k] - r_refit[k] for k in r_refit}
        out[target] = {"ratio_refit": r_refit, "ratio_transferred": r_moved, "gap": gap,
                       "pass": bool(gap["A4"] < gap["A3"] and gap["A5"] < gap["A3"])}
    out["pass"] = bool(all(out[t]["pass"] for t in cfg.transfer_targets)) \
        if cfg.transfer_targets else False
    return out


def _variant_summary(cell: Cell, rules: FittedRules, config: StudyConfig) -> dict:
    """Key statistics of a robustness variant."""
    _, scores = _evaluate(cell, rules, config)
    h2a = an.h2a_separation(cell, config)
    h2c = an.h2c_state_dependence(scores, config)
    profile = deployable_profile(cell.splits["test"].evals, rules.proxies, cell.noise,
                                 config.steps_per_lyapunov)
    regret = regime_regret(rules.regimes[rules.chosen_regimes], profile,
                           cell.splits["test"].moments, config.reference_horizon - 1)[1]
    ref = config.reference_horizon - 1
    return {"H1c": an.h1c_seed_amplifier(cell, config),
            "H2a_median_range": h2a["median_range"], "H2a_partial_corr": h2a["partial_corr"],
            "A4_vs_A2_relative": h2c["A4_minus_A2"]["relative"],
            "A4_over_A3": float(scores["A4"].mse[ref] / scores["A3"].mse[ref]),
            "A5_regret_ratio": regret, "chosen_K": rules.chosen_regimes,
            "mse_href": {k: float(v.mse[ref]) for k, v in scores.items()}}


def _perturbation_scale_variant(study: Study, cell: Cell, rules: FittedRules,
                                scale: float) -> dict:
    """Replace ``Lambda_bar`` and ``Lambda_hat`` by finite-amplitude ``Lambda_fin``."""
    cfg = study.config
    ctx = cell.ctx
    window = cfg.steps_per_lyapunov
    eps = scale * cell.noise
    fin = make_finite_growth(cell.setup.model_step, ctx.spec.observed_index, ctx.obs_scale,
                             ctx.unwhiten, window, cfg.perturbation_dirs, cfg.seed)
    test = cell.splits["test"]
    true_states = ctx.eval_states[ctx.split_indices["test"]]
    oracle_growth = np.concatenate([np.asarray(fin(jnp.asarray(true_states[i:i + 200]), eps))
                                    for i in range(0, len(true_states), 200)])
    m = test.moments
    w_ref = np.clip(oracle_weight(m)[:, m.at(cfg.reference_horizon)], 0.01, 0.99)
    controls = np.column_stack([np.log(m.analog_seed / cell.noise),
                                np.log(m.est_seed / cell.noise)])
    stat = lambda idx: partial_correlation(np.log(w_ref / (1 - w_ref))[idx],
                                           oracle_growth[idx] * window, controls[idx])
    est, lo, hi = block_bootstrap(stat, len(w_ref), cfg.bootstrap_resamples,
                                  cfg.bootstrap_block, cfg.seed)
    agreement = float(np.corrcoef(oracle_growth, cell.oracles["test"].growth)[0, 1])
    return {"scale_times_rho": scale, "H2a_partial_corr_fin": est, "ci": [lo, hi],
            "corr_fin_vs_linear": agreement}


def run_robustness(study: Study, system: str) -> dict:
    """Stage (v): robustness variants at the core cell of one system.

    Parameters
    ----------
    study : Study
        Study.
    system : str
        System name.

    Returns
    -------
    dict
        Variant label to summary statistics.
    """
    cfg = study.config
    out: dict = {"base": _variant_summary(study.core_cells[system], study.fitted[system], cfg)}
    variants: list[tuple[str, dict]] = []
    variants += [(f"D={d}", {"embed_dim": d}) for d in cfg.robustness_dims
                 if d != cfg.embedding_dim and d >= study.context(system).spec.dim]
    variants.append(("delay/2", {"delay_scale": 0.5}))
    variants += [(f"k={k}", {"n_analogs": k}) for k in cfg.analog_counts if k != 1]
    variants += [(f"misspec={p:g}", {"misspec": p}) for p in cfg.misspec_levels]
    for label, kwargs in variants:
        try:
            cell = study.run_cell(system, cfg.core_noise, cfg.core_library, core=True,
                                  with_evals=True, label=label, **kwargs)
            out[label] = _variant_summary(cell, fit_rules([cell], cfg), cfg)
        except Exception as exc:  # noqa: BLE001 - a failed variant is reported, not fatal
            LOG.exception("variant %s failed", label)
            out[label] = {"error": repr(exc)}
    for scale in cfg.perturbation_scales:
        out[f"Lambda_fin(eps={scale:g}rho)"] = _perturbation_scale_variant(
            study, study.core_cells[system], study.fitted[system], scale)
    return out
