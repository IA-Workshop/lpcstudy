"""Validation gate: checks that the code works before results are trusted.

Before any hypothesis is tested, the study checks the machinery itself. Checks
V1-V6 run before the experiments and V7 after experiment E1:

* V1 compares automatic-differentiation Jacobians with finite differences;
* V2 checks that the state estimator reaches the Cramer-Rao floor (the
  smallest error any unbiased estimator can reach) at small noise;
* V3 reports the analog forecaster's valid-prediction time as a sanity
  reference against published values;
* V5 checks the Kaplan-Meier survival estimator on data with a known answer;
* V6 checks the RK4 flow map by halving the step.

(V4, the convergence check, is computed elsewhere; V7, the estimator
efficiency, is in ``analysis.py``.) ``gate_status`` turns the numbers into
pass/fail flags.

The module also holds a separate verification of Theorem P2(c), a bound on
how much observation noise moves the retrieved analog (``check_p2_bound``).
It is report-only: it is not a hypothesis test and not part of the gate.

``experiments.py`` calls these checks. They use ``dynamics.py`` (delay map,
amplification, observability), ``ensemble.py`` (forecasts and the analog
library), ``statistics.py`` (Kaplan-Meier) and ``systems.py`` (flow maps).
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
from scipy import special

from .data import SystemContext
from .dynamics import delay_map_forward, make_amplification, make_observability
from .ensemble import (
    AnalogLibrary,
    ForecastSetup,
    retrieval_spread,
    worker_count,
)
from .oracle import realized_horizon
from .statistics import kaplan_meier
from .systems import make_flow_step, simulate_trajectory


def check_jacobians(
    ctx: SystemContext, n_states: int = 10, horizon: int = 30
) -> dict[str, float]:
    """V1: compare automatic Jacobians with central finite differences.

    A central finite difference estimates a derivative as
    ``(f(s + h) - f(s - h)) / (2h)``; it is slow but independent of the
    automatic-differentiation machinery, so agreement is good evidence that
    the Jacobians are right.

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
        Largest relative errors for the delay-map Jacobian ``A`` and for
        ``g_H``.
    """
    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fwd = delay_map_forward(
        step,
        ctx.spec.observed_index,
        ctx.obs_mean,
        ctx.obs_scale,
        ctx.delay,
        ctx.embed_dim,
    )
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
            fd[:, j] = (
                np.asarray(fwd(jnp.asarray(s_old + e)))
                - np.asarray(fwd(jnp.asarray(s_old - e)))
            ) / (2 * h)
        worst_a = max(
            worst_a, float(np.max(np.abs(auto - fd)) / np.max(np.abs(auto)))
        )

    amp = make_amplification(
        step, ctx.spec.observed_index, ctx.obs_scale, ctx.unwhiten, horizon
    )
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
            row[j] = (
                obs_after(state + h * direction)
                - obs_after(state - h * direction)
            ) / (2 * h)
        worst_g = max(worst_g, abs(np.linalg.norm(row) - gain) / gain)
    return {"delay_jacobian_rel_err": worst_a, "gain_rel_err": worst_g}


def check_cramer_rao(
    ctx: SystemContext,
    noise: float = 1e-4,
    n_states: int = 5,
    n_draws: int = 200,
    seed: int = 0,
) -> dict[str, float]:
    """V2: Gauss-Newton least squares attains ``rho^2 nu^2`` at small noise.

    The estimate is computed in the forward parametrization (oldest window
    state), then mapped to ``s_t`` by the flow; no backward integration is
    used.

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
    The default seed is a fixed literal (0) on purpose: V2 is a verification
    fixture, a deterministic comparison against the Cramer-Rao bound that must
    not move with the study seed, so it stays outside the ``make_rng``
    convention (WU-0002.11, DEF-0011, Q7).
    """
    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fwd = delay_map_forward(
        step,
        ctx.spec.observed_index,
        ctx.obs_mean,
        ctx.obs_scale,
        ctx.delay,
        ctx.embed_dim,
    )
    jac = jax.jit(jax.jacfwd(fwd))
    fwd_j = jax.jit(fwd)
    advance = jax.jit(
        lambda s: jax.lax.fori_loop(0, ctx.history, lambda _, x: step(x), s)
    )
    nu_fn = make_observability(
        step,
        ctx.spec.observed_index,
        ctx.obs_scale,
        ctx.whiten,
        ctx.delay,
        ctx.embed_dim,
    )
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
    return {
        "crlb_ratio_median": float(np.median(ratios)),
        "crlb_ratio_min": float(np.min(ratios)),
        "crlb_ratio_max": float(np.max(ratios)),
    }


def check_kaplan_meier(
    seed: int = 0, n_samples: int = 20_000, horizon_max: int = 60
) -> dict[str, float]:
    """V5: compare Kaplan-Meier with the exact survival of geometric times.

    Event times are geometric (a constant chance of failure per step) and are
    censored at random times and at the horizon ``horizon_max``. The exact
    survival curve is ``(1 - hazard)^t``, so the estimator can be checked
    against a known answer.

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
    The default seed is a fixed literal (0) on purpose: V5 is a verification
    fixture whose comparison with the exact survival must not move with the
    study seed, so it stays outside the ``make_rng`` convention (WU-0002.11,
    DEF-0011, Q7).
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


def check_integrator(
    ctx: SystemContext, n_states: int = 20, horizon: int = 30
) -> dict[str, float]:
    """V6: step-halving check of the RK4 flow map over one Lyapunov time.

    The flow map is run with the normal step and with half that step. For a
    fourth-order method the two results should agree closely if the step is
    small enough.

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
    fine = make_flow_step(
        replace(ctx.spec, max_dt=ctx.spec.max_dt / 2),
        ctx.spec.params,
        ctx.interval,
    )
    worst = 0.0
    for t in ctx.split_indices["test"][:n_states]:
        a = simulate_trajectory(
            coarse, jnp.asarray(ctx.eval_states[t]), horizon + 1
        )
        b = simulate_trajectory(
            fine, jnp.asarray(ctx.eval_states[t]), horizon + 1
        )
        worst = max(
            worst,
            float(
                np.max(
                    np.abs(
                        a[:, ctx.spec.observed_index]
                        - b[:, ctx.spec.observed_index]
                    )
                )
            ),
        )
    return {"integrator_max_dev_sigma": worst / ctx.obs_scale}


def check_cp_horizon(
    setup: ForecastSetup,
    library: AnalogLibrary,
    unit_noise: np.ndarray,
    verify_unit: np.ndarray,
    horizon_max: int,
    theta: float,
    steps_per_lyapunov: int,
    reference_horizon: int | None = None,
) -> dict:
    """V3: report the CP valid-prediction time (sanity reference).

    The valid-prediction time is how long the forecast stays within the
    tolerance ``theta``. It is a sanity reference against Zhang & Gilpin and
    is reported only, not gated.

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
        ``cp_median_vpt_lyapunov``: Kaplan-Meier median CP horizon in
        Lyapunov times; and ``handling``: the counts of the forecasts
        (``handled`` column sums, ``clip_entries``, sizes, the noise level,
        ``D - m`` and the Levenberg-Marquardt arrays of the estimates) for the
        caller to record and pop, so that no leaf is added to the validation
        result. Only the CP clip can affect this check (PLP is computed and
        unused), so the PLP counters of that record are inert.
    """
    from .ensemble import DRAW_COLUMN, DRAW_COUNTERS, forecast_draws

    horizons = np.arange(1, horizon_max + 1)
    rows = np.arange(len(unit_noise))
    batch = forecast_draws(
        setup, library, "test", rows, unit_noise, horizons, reference_horizon
    )
    err = batch.cp_err[:, 0] - setup.noise * verify_unit[:, 0]
    dur, ev = realized_horizon(err, horizons, theta)
    return {
        "cp_median_vpt_lyapunov": kaplan_meier(dur, ev, horizon_max).median()
        / steps_per_lyapunov,
        "handling": {
            "handled": {
                name: int(batch.handled[:, DRAW_COLUMN[name]].sum())
                for name in DRAW_COUNTERS
            },
            "clip_entries": dict(batch.clip_entries),
            "n_states": len(rows),
            "n_draws": unit_noise.shape[1],
            "n_horizons": len(horizons),
            "noise": setup.noise,
            "dof": setup.ctx.embed_dim - setup.ctx.spec.dim,
            "lm": (batch.lm_residual, batch.lm_accepted, batch.lm_late),
        },
    }


def gate_status(validation: dict, v7: dict) -> dict[str, bool]:
    """Return the pass flags of the validation gate.

    The gate covers V1, V2, V4, V5, V6 and V7; V3 is reported only. V7
    (estimator efficiency, :func:`lpcstudy.analysis.v7_efficiency`) needs the
    noise sweep of E1, so the gate is final only after E1 (WU-0002.10).

    Parameters
    ----------
    validation : dict
        Validation results of one system (V1-V6).
    v7 : dict
        The V7 result of the same system; its ``"pass"`` flag is the V7 flag.

    Returns
    -------
    dict[str, bool]
        Flag per check and the overall ``"gate_pass"`` (all of V1, V2, V4, V5,
        V6, V7).
    """
    flags = {
        "V1": validation["delay_jacobian_rel_err"] < 1e-4
        and validation["gain_rel_err"] < 1e-4,
        "V2": 0.8 <= validation["crlb_ratio_median"] <= 1.2,
        "V4": bool(validation["convergence"]["pass"]),
        "V5": validation["km_max_abs_dev"] < 0.01,
        "V6": validation["integrator_max_dev_sigma"] < 1e-3,
        "V7": bool(v7["pass"]),
    }
    flags["gate_pass"] = all(flags.values())
    return {k: bool(v) for k, v in flags.items()}


# ---------------------------------------------------------------------------
# Verification of Theorem P2(c) (WU-0005.5): N against the bound, state by
# state. Not a hypothesis test and not part of the validation gate;
# report-only (a violation is a defect, never a mark).
# ---------------------------------------------------------------------------
P2C_KAPPA: float = 1e-13
"""Relative slack on the k-d tree distance relations (WU-0005.5a, M4).

It is about 450 unit round-offs, and 22 times the first-order bound
``20 u (r2 + ||eta||)`` on the round-off of a computed ``Delta``.
"""

UNIT_ROUNDOFF: float = 2.0**-53
"""Unit round-off ``u`` of IEEE float64, used in the bound ``tau_N``."""

P2C_KIND: str = (
    "verification check (NVVUQ.14, v3 Theorem P2(c)); not a hypothesis test; "
    "no verdict; not in the validation gate"
)

P2C_FORM: str = (
    "N_M^2 <= A_M <= B_M on the same M draws (the empirical law of the draws "
    "is a law of eta, so P2(c) holds for it exactly); the population form "
    "B_inf and z_B are report-only"
)


def chi_tail_moment(
    order: int | float, threshold: float | np.ndarray, dim: int
) -> float | np.ndarray:
    """Return ``E[chi_D^j 1{chi_D >= t}]`` in closed form (WU-0005.5a, M6).

    Here ``chi_D`` is the length of a standard normal vector in ``D``
    dimensions. With ``s = c^2 / 2`` in the chi density the moment is
    ``2^(j/2) Gamma((D+j)/2) / Gamma(D/2) * Q((D+j)/2, t^2/2)``, where ``Q``
    is the regularized upper incomplete gamma function.

    Parameters
    ----------
    order : int or float
        The moment order ``j``.
    threshold : float or np.ndarray
        The lower limit ``t >= 0`` of the chi variable.
    dim : int
        The degrees of freedom ``D``.

    Returns
    -------
    float or np.ndarray
        The moment (``1`` for ``j = 0, t = 0``; ``D`` for ``j = 2, t = 0``).
    """
    return (
        2.0 ** (order / 2)
        * special.poch(dim / 2, order / 2)
        * special.gammaincc((dim + order) / 2, np.asarray(threshold) ** 2 / 2)
    )


def p2_bound_population(
    r1: np.ndarray, delta: np.ndarray, noise: float, dim: int
) -> tuple[np.ndarray, np.ndarray]:
    """Return the population bound ``B_inf`` of P2(c) and a term's variance.

    ``B_inf = 4 / (rho^2 D) * E[(r1 + ||eta||)^2 1{||eta|| >= Delta/2}]`` for
    ``eta ~ N(0, rho^2 I_D)``, so ``||eta|| / rho ~ chi_D``. With
    ``G_j = chi_tail_moment(j, t, D)`` and ``t = Delta / (2 rho)`` it is
    ``4 / (rho^2 D) (r1^2 G0 + 2 r1 rho G1 + rho^2 G2)``. The per-draw term
    ``b_r`` has ``Var(b_r) = (4 / (rho^2 D))^2 (m2 - m1^2)`` with
    ``m2 = sum_k C(4, k) r1^(4-k) rho^k G_k``; the Monte Carlo variance of
    ``B_M`` (the mean of ``M`` terms) is ``Var(b_r) / M``. Both are
    report-only (v3 Theorem P2(c), Methods v2 M5).

    Parameters
    ----------
    r1 : np.ndarray
        Distance to the nearest library vector, per state.
    delta : np.ndarray
        Gap ``r2 - r1`` to the second nearest, per state (``>= 0``).
    noise : float
        Noise level ``rho``.
    dim : int
        Delay dimension ``D``.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        ``B_inf`` and ``Var(b_r)`` per state. The variance is a difference of
        two terms and loses digits when it is small relative to ``m2``; it is
        used in a sum over states only.
    """
    tail = delta / (2.0 * noise)
    moments = [chi_tail_moment(k, tail, dim) for k in range(5)]
    first = (
        r1**2 * moments[0] + 2 * r1 * noise * moments[1] + noise**2 * moments[2]
    )
    second = sum(
        special.comb(4, k) * r1 ** (4 - k) * noise**k * moments[k]
        for k in range(5)
    )
    scale = 4.0 / (noise**2 * dim)
    return scale * first, scale**2 * (second - first**2)


def p2_bound_terms(
    library: AnalogLibrary,
    clean: np.ndarray,
    unit_noise: np.ndarray,
    noise: float,
) -> dict[str, np.ndarray]:
    """Compute the terms of Theorem P2(c) for a set of states.

    The terms are those of v3 section 3 and Methods v2 section M5, computed
    on the production retrieval path.

    For each clean query ``x`` (row of ``clean``) the function takes the draws
    ``q_r = x + rho z_r`` exactly as ``forecast_draws`` forms them, retrieves
    ``Y_r`` through ``AnalogLibrary.query`` and ``analog_vectors`` (k = 1),
    and evaluates, with ``X_1`` the nearest library vector to ``x`` at
    distance ``r1``, ``r2`` the second, ``Delta = r2 - r1`` and
    ``eta_r = ||q_r - x||``:

    * ``N_M``: ``retrieval_spread`` of the ``Y_r`` (the code's N, same draws);
    * ``A_M = mean ||Y_r - X_1||^2 / (rho^2 D)``;
    * ``B_M = 4 mean (r1 + eta_r)^2 1{eta_r >= Delta/2} / (rho^2 D)``, the
      theorem's bound on the same draws; ``B_sw`` the same with
      ``1{Y_r is not X_1}`` as indicator (reported only);
    * ``B_plus``: ``B_M`` with the indicator widened by
      ``s_r = kappa (r2 + eta_r)``, the bound used to check (round-off safe,
      WU-0005.5a M4).

    In exact arithmetic ``N_M^2 <= A_M <= B_M`` for every state and every
    ``M`` (Huygens, the per-draw triangle inequality and P2(a)). The per-state
    checks are counted in the ``n_*`` and ``fail_*`` arrays; none is a
    tolerance to tune (``P2C_KAPPA``, ``tau_N``).

    ``X_1`` is read from ``library.tree.data`` at the tree position of the
    clean query, not through ``analog_vectors``, and ``eta_r`` is recomputed
    from the very array ``q`` that is queried; this gives the chain checks
    power against an indexing defect (WU-0005.5a, M3).

    Parameters
    ----------
    library : AnalogLibrary
        The library (a fixed set of noisy vectors).
    clean : np.ndarray
        Clean query delay vectors ``(n, D)``.
    unit_noise : np.ndarray
        Standard-normal query noise ``(n, M, D)``.
    noise : float
        Query noise level ``rho`` (``> 0``).

    Returns
    -------
    dict[str, np.ndarray]
        Per-state arrays (length ``n``): ``r1``, ``r2``, ``delta``, ``n_m``,
        ``a_m``, ``b_m``, ``b_sw``, ``b_plus``, ``tau``
        (``tau_N = M u max|Y| / rho``), ``center``
        (``||Ybar - X_1||^2 / (rho^2 D)``), ``max_ratio`` (largest
        ``||Y_r - X_1|| / (2 (r1 + eta_r))``), ``eta_sq``
        (``sum_r eta_r^2``), ``n_switch`` (draws with ``Y_r`` not the nearest
        vector), ``n_p2a``, ``n_triangle``, ``n_consistency``, ``n_band``
        (draw counts), ``fail_n_le_a``, ``fail_a_le_b``, ``fail_headline`` and
        ``violation`` (booleans).

    Raises
    ------
    ValueError
        If the shapes disagree, ``noise <= 0`` or the library holds fewer than
        two vectors.
    FloatingPointError
        If a ratio has a zero denominator (``r1 = 0`` and ``eta = 0``),
        instead of a silent inf.
    """
    data = library.tree.data
    if (
        unit_noise.ndim != 3
        or clean.ndim != 2
        or len(clean) != len(unit_noise)
        or unit_noise.shape[2] != clean.shape[1]
        or data.shape[1] != clean.shape[1]
    ):
        raise ValueError(
            f"shapes disagree: clean {clean.shape}, "
            f"unit_noise {unit_noise.shape}, library vectors {data.shape}"
        )
    if not noise > 0:
        raise ValueError(f"noise must be positive, got {noise}")
    if len(data) < 2:
        raise ValueError("P2(c) needs a library of at least two vectors")
    n_states, n_draws, dim = unit_noise.shape
    kappa = P2C_KAPPA

    # The clean query: r1, r2 and X_1 straight from the tree.
    dist_clean, pos_clean = library.tree.query(
        clean, k=2, workers=worker_count()
    )
    r1, r2 = dist_clean[:, 0], dist_clean[:, 1]
    delta = r2 - r1
    nearest = data[pos_clean[:, 0]]

    # The noisy queries and their retrieval, as forecast_draws does it.
    queries = clean[:, None, :] + noise * unit_noise
    eta = np.linalg.norm(queries - clean[:, None, :], axis=-1)
    lib_idx, dist_tree = library.query(queries.reshape(-1, dim), 1)
    retrieved = library.analog_vectors(lib_idx).reshape(n_states, n_draws, dim)
    dist_tree = dist_tree.reshape(n_states, n_draws)
    switched = (
        lib_idx.reshape(n_states, n_draws)
        != library.indices[pos_clean[:, 0]][:, None]
    )

    dist_nearest = np.linalg.norm(retrieved - nearest[:, None, :], axis=-1)
    dist_query = np.linalg.norm(queries - retrieved, axis=-1)
    slack = kappa * (r2[:, None] + eta)
    half = delta[:, None] / 2
    scale = 1.0 / (noise**2 * dim)
    squared = (r1[:, None] + eta) ** 2
    a_m = scale * np.mean(dist_nearest**2, axis=-1)
    b_m = 4 * scale * np.mean(squared * (eta >= half), axis=-1)
    b_sw = 4 * scale * np.mean(squared * switched, axis=-1)
    b_plus = 4 * scale * np.mean(squared * (eta >= half - slack), axis=-1)
    n_m = retrieval_spread(retrieved, noise)
    tau = n_draws * UNIT_ROUNDOFF * np.abs(retrieved).max(axis=(1, 2)) / noise
    center = scale * np.sum((retrieved.mean(axis=1) - nearest) ** 2, axis=-1)
    with np.errstate(divide="raise", invalid="raise"):
        max_ratio = (dist_nearest / (2 * (r1[:, None] + eta))).max(axis=1)

    n_consistency = (
        np.abs(dist_query - dist_tree)
        > kappa * np.maximum(dist_query, dist_tree)
    ).sum(axis=1) + (
        np.abs(np.linalg.norm(clean - nearest, axis=-1) - r1) > kappa * r1
    )
    fail_n_le_a = n_m**2 > a_m * (1 + kappa) + tau**2
    fail_a_le_b = a_m > b_plus * (1 + 4 * kappa)
    fail_headline = n_m**2 > b_plus * (1 + 5 * kappa) + tau**2
    n_p2a = (switched & (eta < half - slack)).sum(axis=1)
    n_triangle = (dist_nearest > 2 * (r1[:, None] + eta) * (1 + kappa)).sum(
        axis=1
    )
    violation = (
        fail_n_le_a
        | fail_a_le_b
        | fail_headline
        | (n_p2a > 0)
        | (n_triangle > 0)
        | (n_consistency > 0)
    )
    return {
        "r1": r1,
        "r2": r2,
        "delta": delta,
        "n_m": n_m,
        "a_m": a_m,
        "b_m": b_m,
        "b_sw": b_sw,
        "b_plus": b_plus,
        "tau": tau,
        "center": center,
        "max_ratio": max_ratio,
        "eta_sq": np.sum(eta**2, axis=1),
        "n_switch": switched.sum(axis=1),
        "n_p2a": n_p2a,
        "n_triangle": n_triangle,
        "n_consistency": n_consistency,
        "n_band": (np.abs(eta - half) <= slack).sum(axis=1),
        "fail_n_le_a": fail_n_le_a,
        "fail_a_le_b": fail_a_le_b,
        "fail_headline": fail_headline,
        "violation": violation,
    }


def pool_terms(parts: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    """Concatenate the per-state arrays of several ``p2_bound_terms`` results.

    This is used, for example, to pool the splits of one cell.
    """
    return {
        key: np.concatenate([part[key] for part in parts]) for key in parts[0]
    }


def _spread(values: np.ndarray) -> dict:
    """Return the median, 90th percentile, maximum and count of ``values``.

    The statistics are ``None`` if ``values`` is empty.
    """
    if len(values) == 0:
        return {"n_states": 0, "median": None, "p90": None, "max": None}
    return {
        "n_states": int(len(values)),
        "median": float(np.median(values)),
        "p90": float(np.quantile(values, 0.9)),
        "max": float(np.max(values)),
    }


def p2_bound_summary(
    terms: dict[str, np.ndarray], noise: float, n_draws: int, dim: int
) -> dict:
    """Summarize pooled ``p2_bound_terms`` as JSON-ready numbers.

    The result holds the ``verification.P2c`` fields.

    Counts of states: ``n_violations`` (a state failing the headline
    ``N^2 <= B_plus (1 + 5k) + tau_N^2`` or any chain item),
    ``n_headline_violations`` and ``n_chain_violations`` (``N_le_A``,
    ``A_le_B``, ``p2a``, ``triangle``, ``consistency``: states with at least
    one failure). ``n_switching_states`` (some draw retrieves another vector),
    ``n_zero_bound_states`` (``B_M == 0``), ``n_ties`` (states with
    ``Delta <= kappa r2``, indistinguishable from a tie; the bound holds for
    ties) and ``n_band_draws`` (draws within the slack of the threshold, about
    1e-12 per draw expected). Tightness: ``N / sqrt(B_M)`` over the states
    with ``B_M > 0``, and the medians of ``N^2/A``, ``A/B_sw`` and ``B_sw/B``
    over the switching states with ``A > 0`` and ``B > 0`` (``n_states`` says
    how many). ``population`` holds ``sum N^2 / sum B_inf`` and
    ``z_B = (sum B_M - sum B_inf) / sqrt(sum Var(b) / M)`` (``None`` if the
    denominator is not positive); no per-state count against ``B_inf`` is
    reported, it has no pass/fail meaning (WU-0005.5a, M2).
    ``noise_second_moment`` is the mean of ``||eta||^2 / (D rho^2)`` over all
    draws with its standard error ``sqrt(2 / (n M D))``.

    Parameters
    ----------
    terms : dict[str, np.ndarray]
        Pooled output of :func:`p2_bound_terms`.
    noise : float
        Query noise level ``rho``.
    n_draws : int
        Draws per state ``M``.
    dim : int
        Delay dimension ``D``.

    Returns
    -------
    dict
        The summary (plain Python types).
    """
    n_states = len(terms["r1"])
    switching = terms["n_switch"] > 0
    positive = terms["b_m"] > 0
    ratio_states = switching & positive & (terms["a_m"] > 0)
    b_inf, variance = p2_bound_population(
        terms["r1"], terms["delta"], noise, dim
    )
    sum_b_inf, sum_var = float(b_inf.sum()), float(variance.sum())
    out_population = {
        "sum_ratio_inf": (
            float(np.sum(terms["n_m"] ** 2) / sum_b_inf)
            if sum_b_inf > 0
            else None
        ),
        "z_B": (
            float((terms["b_m"].sum() - sum_b_inf) / np.sqrt(sum_var / n_draws))
            if sum_var > 0
            else None
        ),
    }
    n, a, b, bsw = (
        terms[k][ratio_states] for k in ("n_m", "a_m", "b_m", "b_sw")
    )
    return {
        "kind": P2C_KIND,
        "form": P2C_FORM,
        "n_states": int(n_states),
        "n_violations": int(terms["violation"].sum()),
        "fraction_violations": float(terms["violation"].mean()),
        "n_headline_violations": int(terms["fail_headline"].sum()),
        "n_chain_violations": {
            "N_le_A": int(terms["fail_n_le_a"].sum()),
            "A_le_B": int(terms["fail_a_le_b"].sum()),
            "p2a": int((terms["n_p2a"] > 0).sum()),
            "triangle": int((terms["n_triangle"] > 0).sum()),
            "consistency": int((terms["n_consistency"] > 0).sum()),
        },
        "n_switching_states": int(switching.sum()),
        "fraction_switching_draws": float(
            terms["n_switch"].sum() / (n_states * n_draws)
        ),
        "n_zero_bound_states": int((~positive).sum()),
        "n_ties": int((terms["delta"] <= P2C_KAPPA * terms["r2"]).sum()),
        "n_band_draws": int(terms["n_band"].sum()),
        "tightness": {
            "N_over_sqrt_B": _spread(
                terms["n_m"][positive] / np.sqrt(terms["b_m"][positive])
            ),
            "median_N2_over_A": _spread(n**2 / a)["median"],
            "median_A_over_Bsw": _spread(a / bsw)["median"],
            "median_Bsw_over_B": _spread(bsw / b)["median"],
            "n_ratio_states": int(ratio_states.sum()),
        },
        "population": out_population,
        "noise_second_moment": {
            "value": float(
                terms["eta_sq"].sum() / (n_states * n_draws * dim * noise**2)
            ),
            "se": float(np.sqrt(2.0 / (n_states * n_draws * dim))),
        },
        "tolerances": {
            "kappa": P2C_KAPPA,
            "tau_N": "M u max|Y| / rho per state, u = 2**-53",
            "tau_N_max": float(terms["tau"].max()),
        },
    }


def check_p2_bound(
    library: AnalogLibrary,
    cleans: dict[str, np.ndarray],
    unit_noises: dict[str, np.ndarray],
    noise: float,
    noise_sens: dict[str, np.ndarray] | None = None,
) -> dict:
    """Build the P2(c) verification block for several splits of one cell.

    The block is stored as ``verification.P2c``.

    Parameters
    ----------
    library : AnalogLibrary
        The cell's library.
    cleans : dict[str, np.ndarray]
        Clean query delay vectors ``(n, D)`` per split.
    unit_noises : dict[str, np.ndarray]
        The cell's oracle noise ``(n, M, D)`` per split (the same arrays the
        cell used).
    noise : float
        Query noise level ``rho``.
    noise_sens : dict[str, np.ndarray], optional
        The cell's ``moments.noise_sens`` per split. If given,
        ``same_draws_identical`` says whether the recomputed ``N_M`` equals
        them bitwise (P1: the check uses the same draws); otherwise it is
        ``None`` (not compared).

    Returns
    -------
    dict
        :func:`p2_bound_summary` of the pooled splits plus ``splits`` (states
        per split) and ``same_draws_identical``.
    """
    parts = {
        name: p2_bound_terms(library, cleans[name], unit_noises[name], noise)
        for name in cleans
    }
    first = next(iter(unit_noises.values()))
    out = p2_bound_summary(
        pool_terms(list(parts.values())), noise, first.shape[1], first.shape[2]
    )
    out["splits"] = {name: int(len(part["r1"])) for name, part in parts.items()}
    out["same_draws_identical"] = (
        None
        if noise_sens is None
        else bool(
            all(
                np.array_equal(parts[name]["n_m"], noise_sens[name])
                for name in parts
            )
        )
    )
    return out
