"""Experiment orchestration: stages (i)-(v) of the proposal.

Stage (i)   dynamical-system generation        -> ``Study.context``
Stage (ii)  mechanism validation               -> :func:`run_system` (V1-V6, E1, E2; the gate
                                                  is final after V7, which needs E1)
Stage (iii) allocation and horizon testing     -> :func:`run_system` (E3, E4)
Stage (iv)  state abstraction and benchmarking -> :func:`run_system` (E5)
Stage (v)   robustness                         -> :func:`run_robustness`
"""

from __future__ import annotations

import logging
import time

import jax.numpy as jnp
import numpy as np

from . import analysis as an
from .allocation import deployable_profile, regime_regret
from .config import StudyConfig
from .data import SPLITS, SystemContext, make_rng
from .dynamics import make_finite_growth
from .embedding import delay_vectors
from .ensemble import CORRELATION_FIELDS, DRAW_COLUMN, DRAW_COUNTERS, ENTRY_COUNTERS, \
    AnalogLibrary, forecast_draws
from .identifiers import check_keys
from .oracle import oracle_weight
from .pipeline import ALL_COUNTERS, COUNTER_DENOMINATOR, HANDLING_SCHEMA, Cell, FittedRules, \
    Study, check_record, fit_rules, rule_weights, score_rules
from .provenance import array_digest
from .validation import check_cp_horizon, check_cramer_rao, check_integrator, \
    check_jacobians, check_kaplan_meier, check_p2_bound, gate_status

LOG = logging.getLogger("lpcstudy")


def _sweep_subset(cell: Cell, config: StudyConfig) -> Cell:
    """Core cell restricted to the test-sweep states and the evaluation horizons."""
    from .pipeline import SplitData

    rows = np.arange(config.n_test_sweep)
    cols = np.array(config.eval_horizons) - 1
    test = cell.splits["test"]
    m = test.moments.subset(rows)
    for attr in ("mean_cp", "mean_plp", "sq_cp", "sq_plp", "cross", *CORRELATION_FIELDS):
        if getattr(m, attr) is not None:  # the correlation fields are optional
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
        Median half-width and mean deviation from the largest-``M`` estimate. The handling counts
        of its forecasts (both errors at ``H_ref`` matter here) are recorded on the study under
        the id ``V4-convergence``, not in this dict.
    """
    cfg = study.config
    ctx = cell.ctx
    n = min(cfg.convergence_states, cfg.n_test)
    noise = study.unit_noise(ctx, "test", "convergence", max(cfg.convergence_draws),
                             ctx.embed_dim)[:n]
    library = AnalogLibrary.build(ctx, cell.noise, cell.library_size, cfg.horizon_max)
    horizons = np.array([cfg.reference_horizon])
    cp, plp = [], []
    lm_parts: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    handled = dict.fromkeys(DRAW_COUNTERS, 0)
    clipped = dict.fromkeys(ENTRY_COUNTERS, 0)
    for start in range(0, n, 5):
        rows = np.arange(start, min(n, start + 5))
        batch = forecast_draws(cell.setup, library, "test", rows, noise[rows], horizons,
                               cfg.reference_horizon)
        cp.append(batch.cp_err[:, :, 0])
        plp.append(batch.plp_err[:, :, 0])
        lm_parts.append((batch.lm_residual, batch.lm_accepted, batch.lm_late))
        for name in DRAW_COUNTERS:
            handled[name] += int(batch.handled[:, DRAW_COLUMN[name]].sum())
        for name in ENTRY_COUNTERS:
            clipped[name] += batch.clip_entries[name]
    cp, plp = np.concatenate(cp), np.concatenate(plp)
    study.record_cell(cell.system, cell.label, "V4-convergence",
                      check_record(handled, clipped, n, noise.shape[1], 1, cell.noise,
                                   ctx.embed_dim - ctx.spec.dim,
                                   tuple(np.concatenate([part[i].ravel() for part in lm_parts])
                                         for i in range(3))))

    def weight(c: np.ndarray, p: np.ndarray) -> np.ndarray:
        # The clip to [0, 1] is the definition of the admissible weight (P1), and 1e-300 the floor
        # of oracle_weight; neither is counted here (DEF-0001, J). The errors themselves come from
        # forecast_draws, whose clips are counted in the V4-convergence block.
        num = np.mean(p * (p - c), axis=-1)
        den = np.mean((c - p) ** 2, axis=-1)
        return np.clip(num / np.maximum(den, 1e-300), 0, 1)

    rng = make_rng(cfg.seed, cell.system, "V4-convergence")  # one stream over the M loop
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


def _cp_horizon_check(study: Study, core: Cell, library: AnalogLibrary, vt: np.ndarray,
                      vv: np.ndarray) -> dict:
    """V3 (``check_cp_horizon``) with its handling counts recorded on the study as ``V3-cp-horizon``.

    Only the CP clip count can affect V3 (PLP is computed and not used), so the PLP counters of
    that block are inert; ``log_handling`` says so.
    """
    cfg = study.config
    out = check_cp_horizon(core.setup, library, vt, vv, cfg.horizon_max, 0.4,
                           cfg.steps_per_lyapunov, cfg.reference_horizon)
    study.record_cell(core.system, core.label, "V3-cp-horizon", check_record(**out.pop("handling")))
    return out


def p2c_verification(study: Study, core: Cell, library: AnalogLibrary) -> dict:
    """Theorem P2(c) checked on the core cell, state by state (``verification.P2c``, WU-0005.5).

    A verification check (NVVUQ.14), not a hypothesis test: it carries no verdict and is not part
    of the validation gate. It uses the core cell's library and the same oracle noise draws on
    all three splits, recomputes ``N`` with them and compares it bitwise with the cell's
    ``noise_sens`` (``same_draws_identical``). The checks and their slack are those of
    :func:`lpcstudy.validation.p2_bound_terms`. It draws no new random numbers (the oracle noise
    is regenerated from the same ``make_rng`` labels) and changes no other result.

    A violation, or a mismatch with ``noise_sens``, is a defect and is written to the run log as
    one ``WARNING`` line (PRIME.4); it is never a tolerance to widen.

    Parameters
    ----------
    study : Study
        The study (configuration and the noise generators).
    core : Cell
        The core cell (``k = 1``).
    library : AnalogLibrary
        The core library (built as ``run_cell`` built it).

    Returns
    -------
    dict
        :func:`lpcstudy.validation.check_p2_bound` plus ``cell`` (noise, library size, analogs,
        draws, splits).
    """
    cfg = study.config
    ctx = core.ctx
    if core.setup.n_analogs != 1:
        raise ValueError(f"P2(c) is stated for the single nearest analog, got "
                         f"k = {core.setup.n_analogs}")
    cleans = {s: delay_vectors(ctx.eval_clean, ctx.split_indices[s], ctx.delay, ctx.embed_dim)
              for s in SPLITS}
    noises = {s: study.unit_noise(ctx, s, "oracle", cfg.n_oracle_draws, ctx.embed_dim)
              for s in SPLITS}
    sensitivity = {s: core.splits[s].moments.noise_sens for s in SPLITS}
    out = check_p2_bound(library, cleans, noises, core.noise, sensitivity)
    out["cell"] = {"noise": core.noise, "n_lib": core.library_size, "n_analogs": 1,
                   "draws": cfg.n_oracle_draws, "splits": list(SPLITS)}
    if out["n_violations"] or not out["same_draws_identical"]:
        LOG.warning("%s P2(c) verification FAILED (a defect, not a tolerance): %d of %d states "
                    "violate (chain %s, headline %d), same_draws_identical = %s",
                    core.system, out["n_violations"], out["n_states"], out["n_chain_violations"],
                    out["n_headline_violations"], out["same_draws_identical"])
    LOG.info("%s P2(c) verification: %d of %d states violate, %d switching states",
             core.system, out["n_violations"], out["n_states"], out["n_switching_states"])
    return out


def v7_replacements(noise_cells: dict[float, Cell]) -> dict[str, int]:
    """Estimates with a replaced coordinate per noise level, on the V7 states (``V7`` leaf, N1).

    V7's own non-finite rule never fires, because ``StateEstimator`` replaces a non-finite state
    by the invariant mean upstream (S2). This count, from the oracle draws of the test-sweep
    states of each noise cell, makes those replacements visible next to the V7 result. It is
    reported only; V7 is not changed (WU-0002.11 Q5).

    Parameters
    ----------
    noise_cells : dict[float, Cell]
        The cells of the noise sweep (as passed to ``v7_noise_scaling``).

    Returns
    -------
    dict[str, int]
        ``f"{rho:g}"`` to the count of (state, draw) estimates replaced.
    """
    column = DRAW_COLUMN["invariant_mean_replacements"]
    out = {}
    for rho in sorted(noise_cells):
        handled = noise_cells[rho].splits["test"].moments.handled
        if handled is None:
            raise ValueError(f"the noise cell at rho={rho:g} carries no handled counts")
        out[f"{rho:g}"] = int(handled[:, column].sum())
    return out


RESULT_COUNT_KEYS: frozenset[str] = frozenset({
    "degenerate_fits", "n_covariance_warnings", "n_constant_states", "n_degenerate_pairs",
    "n_dropped_resamples", "n_empty_regimes", "n_excluded_nonfinite", "n_excluded_states",
    "n_exponent_at_bound", "n_failed_resamples", "n_floored", "n_ineligible_states",
    "n_km_not_reached", "n_nonfinite", "n_screened_out", "n_zero_difference", "nan_resamples",
    "range_n_failed_resamples", "zero_variance_corr"})
"""Result keys that are counts of excluded, failed, replaced, dropped or constant cases (DEF-0001);
the walker copies every integer below such a key into ``handling.result_counts``. The result key
stays the authority. Lane .11b added the keys of the statistics counters (``n_dropped_resamples``,
``n_exponent_at_bound``, ``n_covariance_warnings``, ``n_floored``, ``n_constant_states``,
``n_empty_regimes``, ``n_degenerate_pairs``), the WU-0002.9 counts that were not copied yet
(``n_ineligible_states``, ``n_screened_out``) and ``n_zero_difference`` (the states whose paired
change is exactly 0; in H2e a product of the zero-variance convention, since a state that is
zero-variance in both cells has difference 0). Left out: ``n_states`` (a size) and ``n_noncontiguous_states`` (a
property of the H2a(i) statistic)."""


UNCOUNTED_LEAF_KEYS: frozenset[str] = frozenset({"n_states"})
"""Integer leaves below a counted key that are sizes, not handled cases: the walker skips them
(``H2e.zero_variance_corr.<rho>.<n_lib>.n_states`` is a denominator and always nonzero)."""


def collect_result_counts(result: object, path: str = "") -> dict[str, int]:
    """Copy of the integer counts below every key of ``RESULT_COUNT_KEYS`` (a read-only walk).

    The walk descends through dicts and lists. Below a counted key every ``int`` leaf (not a
    ``bool``) is recorded under its path (keys joined by ``/``, since keys such as ``0.01``
    contain dots); other leaves (floats, strings, ``None``) are skipped, and so is every leaf keyed in
    ``UNCOUNTED_LEAF_KEYS`` (``n_states``: a size).

    Parameters
    ----------
    result : object
        A nested result (dicts, lists, scalars).
    path : str, optional
        Path prefix (used by the recursion).

    Returns
    -------
    dict[str, int]
        Path to count.
    """
    out: dict[str, int] = {}

    def leaves(node: object, where: str) -> None:
        if isinstance(node, bool):
            return
        if isinstance(node, (int, np.integer)):
            out[where] = int(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key not in UNCOUNTED_LEAF_KEYS:
                    leaves(value, f"{where}/{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                leaves(value, f"{where}/{i}")

    def walk(node: object, where: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                child = f"{where}/{key}" if where else str(key)
                if key in RESULT_COUNT_KEYS:
                    leaves(value, child)
                else:
                    walk(value, child)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{where}/{i}" if where else str(i))

    walk(result, path)
    return out


_V3_INERT: frozenset[str] = frozenset({
    "invariant_mean_replacements", "nu_replacements", "error_clips_plp", "error_clips_nonfinite",
    "error_clips_plp_href", "error_clips_nonfinite_href", "lm_nonfinite_cost",
    "lm_nonfinite_jacobian"})


def _log_block(system: str, block_id: str, counts: dict, denominators: dict) -> int:
    """One WARNING line per nonzero counter of a block; returns the number of lines."""
    lines = 0
    for name, value in counts.items():
        if not value:
            continue
        key = COUNTER_DENOMINATOR.get(name)
        of = f"{denominators.get(key)} {key}" if key else "no denominator (total)"
        inert = " [inert: V3 uses CP only]" if block_id.startswith("V3-") and name in _V3_INERT \
            else ""
        LOG.warning("handling %s %s: %s = %d of %s%s", system, block_id, name, value, of, inert)
        lines += 1
    return lines


def log_handling(system: str, handling: dict) -> None:
    """Write the ``handling`` of a system to the run log (PRIME.4: a handled case is never silent).

    One ``WARNING`` line per nonzero counter per block, ``handling <system> <block>: <counter> =
    <k> of <denominator>``, and one ``INFO`` summary line. A zero counter writes nothing.
    Blocks: each cell (with its ``evaluation`` and ``fitting`` sub-blocks), each oracle split and
    the fit.

    Parameters
    ----------
    system : str
        System name (for the line text).
    handling : dict
        A ``handling`` block of a system or of its robustness variants.
    """
    lines = blocks = 0
    for block_id, record in handling.get("cells", {}).items():
        for suffix, part in (("", record), ("/evaluation", record.get("evaluation")),
                             ("/fitting", record.get("fitting"))):
            if part:
                blocks += 1
                lines += _log_block(system, block_id + suffix, part["counts"], part["denominators"])
    for split, record in handling.get("oracles", {}).items():
        blocks += 1
        lines += _log_block(system, f"oracles/{split}", record["counts"], record["denominators"])
    if handling.get("fitting"):
        blocks += 1
        lines += _log_block(system, "fitting", handling["fitting"]["counts"],
                            handling["fitting"]["denominators"])
    LOG.info("handling %s: %d nonzero counters in %d blocks", system, lines, blocks)


def run_handling(study: Study, results: dict) -> dict:
    """The run-level ``handling`` block, after the robustness sweep.

    Parameters
    ----------
    study : Study
        The study (its robustness records and failed variants).
    results : dict
        The results so far: ``systems`` (each with its ``handling``) and, if run, ``robustness``.

    Returns
    -------
    dict
        ``schema``; ``totals`` (every counter, the sum over the main systems); ``by_system`` (each
        system's totals); ``robustness`` (per system: ``cells``, ``oracles``, ``result_counts``,
        ``totals``, kept apart from the totals); ``failed_variants`` (robustness variants that
        raised; their result entries read ``{"error": ...}``).
    """
    by_system = {s: dict(r["handling"]["totals"]) for s, r in results["systems"].items()}
    totals = {name: sum(t[name] for t in by_system.values()) for name in ALL_COUNTERS}
    robustness = {}
    n_variants = 0
    for system, variants in results.get("robustness", {}).items():
        robustness[system] = study.robustness_handling(system, collect_result_counts(variants))
        log_handling(f"{system} robustness", robustness[system])
        n_variants += sum(1 for k in variants if k != "base" and not k.startswith("Lambda_fin"))
    failed = sum(len(labels) for labels in study.failed_variants.values())
    if failed:
        LOG.warning("handling run: failed_variants = %d of %d variants (%s)", failed, n_variants,
                    "; ".join(f"{s}: {', '.join(v)}" for s, v in study.failed_variants.items()))
    skipped = sum(len(labels) for labels in study.skipped_variants.values())
    if skipped:  # not in the results block: no schema change (DEF-0025); the log carries it
        LOG.warning("handling run: skipped_variants = %d (%s)", skipped,
                    "; ".join(f"{s}: {', '.join(v)}" for s, v in study.skipped_variants.items()))
    return {"schema": HANDLING_SCHEMA, "totals": totals, "by_system": by_system,
            "robustness": robustness, "failed_variants": failed}


def context_record(ctx: SystemContext) -> dict:
    """Return ``ctx.meta`` plus bitwise digests of the whitening chain (WU-0001.6, DEF-0024).

    The four digests localize a cross-platform difference: ``state_mean_digest`` differs
    upstream of BLAS (the trajectory or numpy's reduction); ``cov_digest`` differs in the
    covariance product (the BLAS kernel); ``whiten_digest`` or ``unwhiten_digest`` alone differs
    in ``eigh`` or the 3 x 3 products. ``ctx.meta`` is not mutated (it is logged and shared by the
    cached context).

    Parameters
    ----------
    ctx : SystemContext
        The system context (``state_mean``, ``state_cov``, ``whiten`` and ``unwhiten`` are
        float64 arrays).

    Returns
    -------
    dict
        A new dict: the meta entries, then ``state_mean_digest``, ``cov_digest``,
        ``whiten_digest`` and ``unwhiten_digest`` (see ``provenance.array_digest``).
    """
    return {**ctx.meta,
            "state_mean_digest": array_digest(ctx.state_mean),
            "cov_digest": array_digest(ctx.state_cov),
            "whiten_digest": array_digest(ctx.whiten),
            "unwhiten_digest": array_digest(ctx.unwhiten)}


def run_system(study: Study, system: str) -> dict:
    """Stages (ii)-(iv) for one core system.

    The validation gate is computed after the noise sweep, because V7 needs it; it is set before
    ``check_keys`` and before any result is written, and nothing is skipped when it fails (the
    results are flagged as provisional).

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
        ``study`` for robustness.
    """
    cfg = study.config
    t0 = time.time()
    ctx = study.context(system)
    res: dict = {"context": context_record(ctx)}

    # Core cell and validation gate.
    core = study.run_cell(system, cfg.core_noise, cfg.core_library, core=True,
                          with_evals=True)
    library = AnalogLibrary.build(ctx, cfg.core_noise, cfg.core_library, cfg.horizon_max)
    vt = study.unit_noise(ctx, "test", "eval", 1, ctx.embed_dim)
    vv = study.unit_noise(ctx, "test", "verify", 1, cfg.horizon_max)
    res["validation"] = {
        **check_jacobians(ctx), **check_cramer_rao(ctx), **check_kaplan_meier(),
        **check_integrator(ctx),
        **_cp_horizon_check(study, core, library, vt, vv),
        "convergence": convergence_check(study, core),
        "estimators": {k: v for k, v in study.estimator_log.items() if system in k}}
    LOG.info("%s validation (V1-V6; the gate is set after V7): %s", system, res["validation"])
    # Verification, not validation: report-only, outside the gate (WU-0005.5, NVVUQ.14).
    res["verification"] = {"P2c": p2c_verification(study, core, library)}

    rules = fit_rules([core], cfg)
    study.record_rules(system, core, rules)
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
    for rho in cfg.noise_levels:
        if rho != cfg.core_noise:
            noise_cells[rho] = study.run_cell(system, rho, cfg.core_library, core=False,
                                              with_evals=False)
    library_cells = {}
    for rho in cfg.library_sweep_noises:
        for size in cfg.library_sizes:
            if rho == cfg.core_noise and size == cfg.core_library:
                library_cells[(rho, size)] = core_sub
                continue
            if size == cfg.core_library and rho in noise_cells:
                library_cells[(rho, size)] = noise_cells[rho]
                continue
            library_cells[(rho, size)] = study.run_cell(system, rho, size, core=False,
                                                        with_evals=False)

    # Hypotheses.
    res["V7"] = an.v7_noise_scaling(noise_cells, cfg)
    res["V7"]["invariant_mean_replacements"] = v7_replacements(noise_cells)
    res["validation"]["gate"] = gate_status(res["validation"], res["V7"])  # V7 needs E1
    if not res["validation"]["gate"]["gate_pass"]:
        LOG.warning("%s: VALIDATION GATE FAILED %s; results are flagged as provisional",
                    system, res["validation"]["gate"])
    LOG.info("%s validation gate: %s", system, res["validation"]["gate"])
    res["H1a"] = an.h1a_library_scaling(library_cells, cfg)
    res["H1b"] = an.h1b_seed_amplifier(core, cfg)
    res["H1c"] = an.h1c_horizon_law(core, cfg)
    res["H1d"] = an.h1d_proxies(core, rules, cfg)
    res["Q-N"] = an.qn_noise_redundancy(core, rules, cfg)
    res["H2a"] = an.h2a_separation(core, cfg)
    res["H2b"] = an.h2b_knob_response(noise_cells, library_cells, cfg)
    res["H2c"] = an.h2c_state_dependence(scores, core.splits["calibration"], cfg, system)
    res["H2d"] = an.h2d_empirical_comparison(scores, cfg, system)
    res["H2e"] = an.h2e_noise_matching(library_cells, cfg)
    res["gain_bound"] = an.gain_horizon_bound(core, cfg)
    res.update(an.h3_regimes(core, rules, scores, cfg))
    res["oracle_recovery"] = an.oracle_recovery(scores, cfg)
    check_keys(res)
    res["handling"] = study.system_handling(system, collect_result_counts(res))
    log_handling(system, res["handling"])
    res["seconds"] = time.time() - t0
    study.core_cells[system] = core
    study.fitted[system] = rules
    LOG.info("%s finished in %.0fs", system, res["seconds"])
    return res


def _variant_summary(cell: Cell, rules: FittedRules, config: StudyConfig) -> dict:
    """Key statistics of a robustness variant."""
    _, scores = _evaluate(cell, rules, config)
    h2a = an.h2a_separation(cell, config)
    h2c = an.h2c_state_dependence(scores, cell.splits["calibration"], config, cell.system)
    profile = deployable_profile(cell.splits["test"].evals, rules.proxies, cell.noise,
                                 config.steps_per_lyapunov)
    regret = regime_regret(rules.regimes[rules.chosen_regimes], profile,
                           cell.splits["test"].moments, config.reference_horizon - 1)[1]
    ref = config.reference_horizon - 1
    out = {"H1b": an.h1b_seed_amplifier(cell, config),
           "H2a_median_range": h2a["median_range"],
           "H2a_partial_corr_zero": h2a["part_ii"]["zero"]["partial_corr"],
           "H2a_partial_corr_interior": h2a["part_ii"]["interior"]["partial_corr"],
           "A4_vs_A2_relative": h2c["A4_minus_A2"]["relative"],
           "A4_over_A3": float(scores["A4"].mse[ref] / scores["A3"].mse[ref]),
           "A5_regret_ratio": regret, "chosen_K": rules.chosen_regimes,
           "mse_href": {k: float(v.mse[ref]) for k, v in scores.items()}}
    check_keys(out)
    return out


def _perturbation_scale_variant(study: Study, cell: Cell, rules: FittedRules,
                                scale: float) -> dict:
    """Replace ``Lambda_bar`` and ``Lambda_hat`` by finite-amplitude ``Lambda_fin``."""
    cfg = study.config
    ctx = cell.ctx
    window = cfg.steps_per_lyapunov
    eps = scale * cell.noise
    # a fresh generator per call, no scale in the label: the same directions at every scale
    # (common random numbers across scales; WU-0002.14, M4)
    fin = make_finite_growth(cell.setup.model_step, ctx.spec.observed_index, ctx.obs_scale,
                             ctx.unwhiten, window, cfg.perturbation_dirs,
                             make_rng(cfg.seed, cell.system, "finite-growth"))
    test = cell.splits["test"]
    true_states = ctx.eval_states[ctx.split_indices["test"]]
    oracle_growth = np.concatenate([np.asarray(fin(jnp.asarray(true_states[i:i + 200]), eps))
                                    for i in range(0, len(true_states), 200)])
    m = test.moments
    w_ref = oracle_weight(m)[:, m.at(cfg.reference_horizon)]
    seeds = np.column_stack([np.log(m.analog_seed / cell.noise),
                             np.log(m.est_seed / cell.noise)])
    # The same two-part statistic and index sets as H2a(ii), with Lambda_fin for Lambda_tilde:
    # the generator labels are those of analysis.h2a_separation, so the resamples are shared.
    two = an.h2a_part_ii(w_ref, oracle_growth * window, seeds,
                         n_resamples=cfg.bootstrap_resamples, block=cfg.bootstrap_block,
                         seed=make_rng(cfg.seed, cell.system, "h2a-two-part"),
                         level=an.PRIMARY_LEVEL)
    agreement = float(np.corrcoef(oracle_growth, cell.oracles["test"].growth)[0, 1])
    return {"scale_times_rho": scale,
            "H2a_partial_corr_zero_fin": two["part_ii"]["zero"]["partial_corr"],
            "H2a_partial_corr_interior_fin": two["part_ii"]["interior"]["partial_corr"],
            "ci_zero": two["part_ii"]["zero"]["ci"], "ci_interior": two["part_ii"]["interior"]["ci"],
            "corr_fin_vs_linear": agreement}


def robustness_dimensions(cfg: StudyConfig, state_dim: int) -> tuple[list[int], list[int]]:
    """Split the configured robustness dimensions into those run and those skipped (DEF-0025).

    A variant needs ``d - state_dim`` positive chi-square degrees of freedom (the goodness-of-fit
    threshold has none at ``d == state_dim``), so the kept dimensions are ``d > state_dim``. The
    base dimension ``cfg.embedding_dim`` is the base cell, neither a variant nor a skip.

    Parameters
    ----------
    cfg : StudyConfig
        Configuration (``robustness_dims`` and ``embedding_dim``).
    state_dim : int
        Dimension of the system (``spec.dim``).

    Returns
    -------
    tuple of list of int
        ``(kept, skipped)``, each in configured order; ``skipped`` holds ``d <= state_dim``.
    """
    candidates = [d for d in cfg.robustness_dims if d != cfg.embedding_dim]
    return [d for d in candidates if d > state_dim], [d for d in candidates if d <= state_dim]


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
    kept, skipped = robustness_dimensions(cfg, study.context(system).spec.dim)
    variants += [(f"D={d}", {"embed_dim": d}) for d in kept]
    for d in skipped:  # counted and reported, never dropped silently (DEF-0025, PRIME.4)
        study.record_skipped_variant(system, f"D={d}")
    if skipped:
        LOG.warning("robustness %s: skipped_variants = %d (%s): dimension not above the state "
                    "dimension, zero chi-square degrees of freedom", system, len(skipped),
                    ", ".join(f"D={d}" for d in skipped))
    variants += [(f"k={k}", {"n_analogs": k}) for k in cfg.analog_counts if k != 1]
    variants += [(f"misspec={p:g}", {"misspec": p}) for p in cfg.misspec_levels]
    for label, kwargs in variants:
        try:
            cell = study.run_cell(system, cfg.core_noise, cfg.core_library, core=True,
                                  with_evals=True, label=label, **kwargs)
            rules = fit_rules([cell], cfg)
            study.record_rules(system, cell, rules)
            out[label] = _variant_summary(cell, rules, cfg)
        except Exception as exc:  # noqa: BLE001 - a failed variant is reported, not fatal
            LOG.exception("variant %s failed", label)
            study.record_failed_variant(system, label)  # counted: handling.failed_variants
            out[label] = {"error": repr(exc)}
    for scale in cfg.perturbation_scales:
        out[f"Lambda_fin(eps={scale:g}rho)"] = _perturbation_scale_variant(
            study, study.core_cells[system], study.fitted[system], scale)
    return out
