"""Validation gate (stage ii prerequisites): V1-V6 run before the experiments; V7 after E1."""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from .data import SystemContext
from .dynamics import delay_map_forward, make_amplification, make_observability
from .ensemble import AnalogLibrary, ForecastSetup
from .oracle import realized_horizon
from .statistics import kaplan_meier
from .systems import make_flow_step, simulate_trajectory


def check_jacobians(ctx: SystemContext, n_states: int = 10, horizon: int = 30
                    ) -> dict[str, float]:
    """V1: automatic Jacobians against central finite differences.

    Parameters
    ----------
    ctx : SystemContext
        System context.
    n_states : int, optional
        States checked.
    horizon : int, optional
        Horizon for ``Gamma_H``.

    Returns
    -------
    dict[str, float]
        Largest relative errors for the delay-map Jacobian ``A`` and for ``g_H``.
    """
    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale,
                            ctx.delay, ctx.embed_dim)
    times = ctx.split_indices["test"][:n_states]
    olds = ctx.eval_states[times - ctx.history]
    scale = np.sqrt(np.diag(ctx.unwhiten @ ctx.unwhiten.T))
    worst_a = 0.0
    for s_old in olds:
        auto = np.asarray(jax.jacfwd(fwd)(jnp.asarray(s_old)))
        fd = np.zeros_like(auto)
        for j in range(len(s_old)):
            h = 1e-6 * scale[j]
            e = np.zeros_like(s_old)
            e[j] = h
            fd[:, j] = (np.asarray(fwd(jnp.asarray(s_old + e)))
                        - np.asarray(fwd(jnp.asarray(s_old - e)))) / (2 * h)
        worst_a = max(worst_a, float(np.max(np.abs(auto - fd)) / np.max(np.abs(auto))))

    amp = make_amplification(step, ctx.spec.observed_index, ctx.obs_scale, ctx.unwhiten,
                             horizon)
    states = ctx.eval_states[times]
    gains = np.asarray(amp(jnp.asarray(states)))[:, -1]

    def obs_after(s: np.ndarray) -> float:
        traj = simulate_trajectory(step, jnp.asarray(s), horizon + 1)
        return float(traj[-1, ctx.spec.observed_index]) / ctx.obs_scale

    worst_g = 0.0
    for state, gain in zip(states, gains):
        row = np.zeros(len(state))
        for j in range(len(state)):
            direction = ctx.unwhiten[:, j]
            h = 1e-6
            row[j] = (obs_after(state + h * direction) - obs_after(state - h * direction)) \
                / (2 * h)
        worst_g = max(worst_g, abs(np.linalg.norm(row) - gain) / gain)
    return {"delay_jacobian_rel_err": worst_a, "gain_rel_err": worst_g}


def check_cramer_rao(ctx: SystemContext, noise: float = 1e-4, n_states: int = 5,
                     n_draws: int = 200, seed: int = 0) -> dict[str, float]:
    """V2: Gauss-Newton least squares attains ``rho^2 nu^2`` in the small-noise limit.

    The estimate is computed in the forward parametrization (oldest window
    state), then mapped to ``s_t`` by the flow; no backward integration is used.

    Parameters
    ----------
    ctx : SystemContext
        System context.
    noise : float, optional
        Small noise level (fraction of ``sigma_x``).
    n_states : int, optional
        States checked.
    n_draws : int, optional
        Monte Carlo draws per state.
    seed : int, optional
        Seed.

    Returns
    -------
    dict[str, float]
        Median and range of ``E||s_hat - s||^2 / (rho^2 nu^2)``.

    Notes
    -----
    The default seed is a fixed literal (0) on purpose: V2 is a verification fixture, a
    deterministic comparison against the Cramer-Rao bound that must not move with the study
    seed, so it stays outside the ``make_rng`` convention (WU-0002.11, DEF-0011, Q7).
    """
    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale,
                            ctx.delay, ctx.embed_dim)
    jac = jax.jit(jax.jacfwd(fwd))
    fwd_j = jax.jit(fwd)
    advance = jax.jit(lambda s: jax.lax.fori_loop(0, ctx.history, lambda _, x: step(x), s))
    nu_fn = make_observability(step, ctx.spec.observed_index, ctx.obs_scale, ctx.whiten,
                               ctx.delay, ctx.embed_dim)
    rng = np.random.default_rng(seed)
    ratios = []
    for t in ctx.split_indices["test"][:n_states]:
        s_old = ctx.eval_states[t - ctx.history]
        s_t = ctx.eval_states[t]
        clean = np.asarray(fwd_j(jnp.asarray(s_old)))
        nu = float(nu_fn(jnp.asarray(s_old[None, :]))[0])
        errs = []
        for _ in range(n_draws):
            target = clean + noise * rng.standard_normal(len(clean))
            est = s_old.copy()
            for _ in range(3):
                a_mat = np.asarray(jac(jnp.asarray(est)))
                resid = target - np.asarray(fwd_j(jnp.asarray(est)))
                est = est + np.linalg.lstsq(a_mat, resid, rcond=None)[0]
            s_hat = np.asarray(advance(jnp.asarray(est)))
            errs.append(np.sum((ctx.whiten @ (s_hat - s_t)) ** 2))
        ratios.append(np.mean(errs) / (noise * nu) ** 2)
    return {"crlb_ratio_median": float(np.median(ratios)),
            "crlb_ratio_min": float(np.min(ratios)), "crlb_ratio_max": float(np.max(ratios))}


def check_kaplan_meier(seed: int = 0, n_samples: int = 20_000, horizon_max: int = 60
                       ) -> dict[str, float]:
    """V5: Kaplan-Meier against the exact survival of censored geometric times.

    Parameters
    ----------
    seed : int, optional
        Seed.
    n_samples : int, optional
        Sample size.
    horizon_max : int, optional
        Administrative censoring horizon.

    Returns
    -------
    dict[str, float]
        Largest absolute deviation from the true survival function.

    Notes
    -----
    The default seed is a fixed literal (0) on purpose: V5 is a verification fixture whose
    comparison with the exact survival must not move with the study seed, so it stays outside
    the ``make_rng`` convention (WU-0002.11, DEF-0011, Q7).
    """
    rng = np.random.default_rng(seed)
    hazard = 0.05
    event_times = rng.geometric(hazard, n_samples)
    censor_times = rng.integers(1, horizon_max + 1, n_samples)
    durations = np.minimum(np.minimum(event_times, censor_times), horizon_max)
    events = (event_times <= censor_times) & (event_times <= horizon_max)
    curve = kaplan_meier(durations, events, horizon_max)
    truth = (1 - hazard) ** curve.times
    return {"km_max_abs_dev": float(np.max(np.abs(curve.survival - truth)))}


def check_integrator(ctx: SystemContext, n_states: int = 20, horizon: int = 30
                     ) -> dict[str, float]:
    """V6: step-halving check of the RK4 flow map over one Lyapunov time.

    Parameters
    ----------
    ctx : SystemContext
        System context.
    n_states : int, optional
        States checked.
    horizon : int, optional
        Steps integrated.

    Returns
    -------
    dict[str, float]
        Largest observable discrepancy (units of ``sigma_x``).
    """
    from dataclasses import replace

    coarse = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fine = make_flow_step(replace(ctx.spec, max_dt=ctx.spec.max_dt / 2), ctx.spec.params,
                          ctx.interval)
    worst = 0.0
    for t in ctx.split_indices["test"][:n_states]:
        a = simulate_trajectory(coarse, jnp.asarray(ctx.eval_states[t]), horizon + 1)
        b = simulate_trajectory(fine, jnp.asarray(ctx.eval_states[t]), horizon + 1)
        worst = max(worst, float(np.max(np.abs(a[:, ctx.spec.observed_index]
                                                - b[:, ctx.spec.observed_index]))))
    return {"integrator_max_dev_sigma": worst / ctx.obs_scale}


def check_cp_horizon(setup: ForecastSetup, library: AnalogLibrary, unit_noise: np.ndarray,
                     verify_unit: np.ndarray, horizon_max: int, theta: float,
                     steps_per_lyapunov: int, reference_horizon: int | None = None) -> dict:
    """V3: CP valid-prediction time (sanity reference against Zhang & Gilpin).

    Parameters
    ----------
    setup : ForecastSetup
        Forecasters (core noise level).
    library : AnalogLibrary
        Core library.
    unit_noise : np.ndarray
        Query noise ``(n, 1, D)``.
    verify_unit : np.ndarray
        Verification noise ``(n, 1, H_max)``.
    horizon_max : int
        ``H_max``.
    theta : float
        Tolerance.
    steps_per_lyapunov : int
        Steps per Lyapunov time.
    reference_horizon : int, optional
        ``H_ref`` in steps, for the H_ref columns of the handling counts.

    Returns
    -------
    dict
        ``cp_median_vpt_lyapunov``: Kaplan-Meier median CP horizon in Lyapunov times; and
        ``handling``: the counts of the forecasts (``handled`` column sums, ``clip_entries``,
        sizes) for the caller to record and pop, so that no leaf is added to the validation
        result. Only the CP clip can affect this check (PLP is computed and unused), so the PLP
        counters of that record are inert.
    """
    from .ensemble import DRAW_COLUMN, DRAW_COUNTERS, forecast_draws

    horizons = np.arange(1, horizon_max + 1)
    rows = np.arange(len(unit_noise))
    batch = forecast_draws(setup, library, "test", rows, unit_noise, horizons, reference_horizon)
    err = batch.cp_err[:, 0] - setup.noise * verify_unit[:, 0]
    dur, ev = realized_horizon(err, horizons, theta)
    return {"cp_median_vpt_lyapunov":
            kaplan_meier(dur, ev, horizon_max).median() / steps_per_lyapunov,
            "handling": {"handled": {name: int(batch.handled[:, DRAW_COLUMN[name]].sum())
                                     for name in DRAW_COUNTERS},
                         "clip_entries": dict(batch.clip_entries), "n_states": len(rows),
                         "n_draws": unit_noise.shape[1], "n_horizons": len(horizons)}}


def gate_status(validation: dict, v7: dict) -> dict[str, bool]:
    """Pass flags of the validation gate (V1, V2, V4, V5, V6, V7; V3 is reported only).

    V7 (estimator efficiency, :func:`lpcstudy.analysis.v7_efficiency`) needs the noise sweep of
    E1, so the gate is final only after E1 (WU-0002.10).

    Parameters
    ----------
    validation : dict
        Validation results of one system (V1-V6).
    v7 : dict
        The V7 result of the same system; its ``"pass"`` flag is the V7 flag.

    Returns
    -------
    dict[str, bool]
        Flag per check and the overall ``"gate_pass"`` (all of V1, V2, V4, V5, V6, V7).
    """
    flags = {
        "V1": validation["delay_jacobian_rel_err"] < 1e-4 and validation["gain_rel_err"] < 1e-4,
        "V2": 0.8 <= validation["crlb_ratio_median"] <= 1.2,
        "V4": bool(validation["convergence"]["pass"]),
        "V5": validation["km_max_abs_dev"] < 0.01,
        "V6": validation["integrator_max_dev_sigma"] < 1e-3,
        "V7": bool(v7["pass"]),
    }
    flags["gate_pass"] = all(flags.values())
    return {k: bool(v) for k, v in flags.items()}
