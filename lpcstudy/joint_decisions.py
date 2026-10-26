"""LPC contribution study, experiment C: one profile, two decisions (WU-0049).

DEVELOPMENT, exploratory: every number is an estimate on a development seed,
read by tables fixed here before any result of C was seen, never passed or
failed. It reuses the WU-0048 machinery of ``lpcstudy.contribution`` (the
learner with inner blocked cross-validation, the losses, the realized
per-draw score, the guards, the shared moving-block index sets) and runs
offline on the state dump of schema /3.

C1, separate performance (:func:`c1_rows`)
    A table read from the A/D record of ``tools/lpc_contrib.py`` (no refit).

C2, shared information, oracle profile (:func:`analyze_joint`), as replaced
by the mathematics specification
    *Forward bottleneck*: the horizon quantile models (the WU-0048 target
    ``Y = ln min(T_c, H_max)`` of the oracle hybrid) fitted on the five
    allocation outputs ``g(F)`` (clipped weights at the five evaluation
    horizons) instead of ``F``; also on each single horizon's output (median
    only). *Reverse bottleneck*: the allocation model at each horizon (u with
    weight ``kappa / mean kappa``, M-2) fitted on the three horizon quantile
    outputs ``h(F)`` instead of ``F``. The bottleneck inputs of the training
    states are cross-fitted (five contiguous time blocks, each block
    predicted by the model fitted, with its own inner cross-validation, on
    the other four), so no training state sees its own target through them;
    the test inputs come from the models fitted on every training state.

    Skill retained: ``[L(constant) - L(bottleneck)] / [L(constant) - L(F)]``
    (pinball at 0.5 for the horizon, the moment-form MSE for allocation),
    with the paired 95% interval of the shared index sets. Reading (fixed in
    advance): "keeps most" if the interval lies above 0.5, "loses most" if
    below; "not determined" if it spans 0.5, if the full model's skill
    ``L(constant) - L(F)`` has a 95% lower bound ``<= 0`` ("full-profile skill
    not established"), if a failed-resample count makes a bound infinite, or
    (allocation) if ``min(Kish(kappa), Kish(excess of F)) < 50``. The MSE
    ratio ``MSE(bottleneck) / MSE(F)`` is also read by the 1.05 table.

    The rank correlation of the Shapley shares of the two decisions (oracle
    profile; allocation ``L_A`` per horizon against the horizon pinball) is
    descriptive: four items, no interval, no test (:func:`shapley_rank_rows`).

C3, the deployable chain (:func:`analyze_joint`)
    Policies, each a weight per (state, draw) on ``1..H_max`` and a trusted
    horizon ``q_0.1`` per (state, draw):

    * ``A2 + constant``: the stored A2 weight (the pooled minimizer on the
      construction moments, rebuilt on ``1..H_max`` and checked bitwise
      against the dumped A2 at the five horizons) and the training 10%
      quantile of its characteristic crossing time;
    * ``A2 + h(F-hat)``: the same weight; quantile models on the deployable
      profile predict its crossing time (C3 step 1);
    * ``A4 + KM leaf``: the stored A4 weight; ``q_0.1`` per A5 leaf
      (``core/a5_leaf``), the Kaplan-Meier 10% quantile (the smallest ``H``
      with ``S(H) <= 0.9``) of the A4 hybrid's characteristic horizon over the
      calibration (state, draw) pairs of the leaf (``a5_leaf_calibration``).
      The run's A5 uses realized horizons there; the dump has no per-draw
      calibration errors on the full grid, so the characteristic horizon
      stands in (stated in every table). A test leaf with no calibration pair
      takes the pooled quantile (counted);
    * ``g(F-hat) + h(F-hat)`` (the full system, C3 step 2): the learned
      deployable allocation (the WU-0048 ``A/ROIN`` model per horizon), its
      five outputs per draw extended to ``1..H_max`` by linear interpolation
      in ``ln H`` (constant beyond 8 and 120 steps; :func:`full_grid_weight`);
      quantile models on the deployable profile, trained on the
      characteristic crossing time of that hybrid per training (state,
      draw), with cross-fitted training weights.

    Training is construction + calibration, as in WU-0048 (the plan's
    "trained on construction" is read as the WU-0048 training rows).

    Joint metrics on the test states: the realized hybrid MSE per evaluation
    horizon (``contribution.realized_score``; ratio to A2 read by the 1.05
    table with the addendum R2 guard); the false-trust rate ``P(T <=
    q_0.1)`` (target 10%), with ``T`` the realized first passage per draw
    (``oracle.realized_horizon`` of ``blend - verify_noise``, the run's
    definition) and, beside it, the characteristic crossing time; the mean
    trusted horizon ``q_0.1`` (Lyapunov times). The trusted horizon is capped
    at ``H_max``; a censored path (``T > H_max``) is then never a false
    trust, so the rate is exact. 95% intervals from the shared index sets.

Randomness: the caller passes the shared index sets of
``contribution.bootstrap_generator`` and the WU-0048 learner (its
scikit-learn seed). No new random number is drawn.

Handled cases are counted: clipped weights, quantile crossings and caps,
empty leaves, ``T = 1`` and ``e_{T-1} = theta`` in ``T_c``, failed fits.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np

from . import contribution as cb
from .ablation import CONDITIONS, subset_key
from .mechanisms import spearman
from .oracle import realized_horizon
from .statistics import kaplan_meier

RETAIN_LEVEL: float = 0.5
"""The retained skill share that separates "keeps most" from "loses most"."""
TRUST_LEVEL: float = 0.1
"""The quantile of the trusted horizon (false-trust target)."""
FULL_KEY: str = subset_key(cb.FULL)
"""``"ROIN"``."""


# ----------------------------------------------------------------- weights
def pooled_weight(
    e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
) -> np.ndarray:
    """A2 on every column: ``clip(sum(E_P - C) / max(sum kappa, 1e-300), 0, 1)``.

    Inputs ``(n, H)`` (the construction moments); result ``(H,)``. The
    arithmetic of ``allocation.global_weight``.
    """
    num = np.sum(e_p - cross, axis=0)
    den = np.sum(e_c + e_p - 2.0 * cross, axis=0)
    return np.clip(num / np.maximum(den, cb.CURVATURE_FLOOR), 0.0, 1.0)


def full_grid_weight(
    weight: np.ndarray, horizons: np.ndarray, h_max: int
) -> np.ndarray:
    """Extend weights at ``horizons`` (last axis) to ``1..h_max``.

    Linear in ``ln H`` between the given horizons, constant before the first
    and after the last (``np.interp``'s rule, row by row). At the given
    horizons the result equals the input exactly.
    """
    grid = np.log(np.arange(1, h_max + 1, dtype=float))
    knots = np.log(np.asarray(horizons, dtype=float))
    upper = np.clip(
        np.searchsorted(knots, grid, side="right"), 1, len(knots) - 1
    )
    lower = upper - 1
    frac = np.clip(
        (grid - knots[lower]) / (knots[upper] - knots[lower]), 0.0, 1.0
    )
    out = weight[..., lower] * (1.0 - frac) + weight[..., upper] * frac
    exact = np.searchsorted(knots, grid)
    hit = (exact < len(knots)) & (
        knots[np.minimum(exact, len(knots) - 1)] == grid
    )
    out[..., hit] = weight[..., exact[hit]]
    return out


def policy_crossing(
    e_c: np.ndarray,
    e_p: np.ndarray,
    cross: np.ndarray,
    weight: np.ndarray,
    noise: float,
    theta: float,
) -> cb.Crossing:
    """Characteristic crossing time of a policy per (state, draw).

    ``e_H = sqrt(V_H(w_H) + rho^2)`` with ``V`` the moment form at the
    policy's own weight; moments ``(n, H)``, weights ``(H,)``, ``(n, H)`` or
    ``(n, r, H)``. The result has shape ``(n, r)`` (``r = 1`` unless the
    weights have three axes). ``ceil(T_c)`` is ``characteristic_horizon`` of
    the same curve.
    """
    w = np.asarray(weight)
    if w.ndim < 3:
        w = np.broadcast_to(w, e_c.shape)[:, None, :]
    mse = cb.quad_mse(w, e_c[:, None, :], e_p[:, None, :], cross[:, None, :])
    return cb.rms_crossing(np.sqrt(mse + noise**2), theta)


def realized_policy_horizon(
    weight: np.ndarray,
    cp_err: np.ndarray,
    plp_err: np.ndarray,
    verify_noise: np.ndarray,
    theta: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Realized first passage per (state, draw), the run's definition.

    ``oracle.realized_horizon`` of ``w e_C + (1 - w) e_P - verify_noise``
    (the blend's error against the noisy truth), as ``pipeline.score_rules``.
    Arrays ``(n, E, H_max)`` (weights broadcast); returns durations and
    events ``(n, E)``.
    """
    blend = weight * cp_err + (1.0 - weight) * plp_err
    horizons = np.arange(1, cp_err.shape[-1] + 1)
    return realized_horizon(blend - verify_noise, horizons, theta)


def km_quantile(
    durations: np.ndarray, events: np.ndarray, h_max: int, level: float
) -> float:
    """The smallest ``H`` with Kaplan-Meier ``S(H) <= 1 - level``.

    ``statistics.kaplan_meier``; ``h_max`` if the curve never falls that low
    (the cap of the trusted horizon).
    """
    curve = kaplan_meier(durations, events, h_max)
    hit = np.nonzero(curve.survival <= 1.0 - level)[0]
    return float(curve.times[hit[0]]) if hit.size else float(h_max)


def leaf_quantiles(
    leaf_cal: np.ndarray,
    durations: np.ndarray,
    events: np.ndarray,
    leaf_test: np.ndarray,
    h_max: int,
    level: float = TRUST_LEVEL,
) -> tuple[np.ndarray, dict]:
    """Per-leaf Kaplan-Meier quantile for every test entry (A5-style).

    Calibration pairs ``(n_cal, E)`` give the curve of each leaf; a test leaf
    without calibration pairs takes the pooled quantile (counted).

    Returns
    -------
    tuple
        The quantile (steps) per test entry, shape of ``leaf_test``, and a
        record (per-leaf quantiles and sizes, fallback counts).
    """
    pooled = km_quantile(durations.ravel(), events.ravel(), h_max, level)
    table: dict[int, float] = {}
    sizes: dict[int, int] = {}
    for leaf in np.unique(leaf_cal):
        rows = leaf_cal == leaf
        table[int(leaf)] = km_quantile(
            durations[rows], events[rows], h_max, level
        )
        sizes[int(leaf)] = int(rows.sum())
    out = np.full(leaf_test.shape, pooled)
    missing = 0
    for leaf in np.unique(leaf_test):
        rows = leaf_test == leaf
        if int(leaf) in table:
            out[rows] = table[int(leaf)]
        else:
            missing += int(rows.sum())
    return out, {
        "quantile_by_leaf": {str(k): v for k, v in table.items()},
        "calibration_pairs_by_leaf": {str(k): v for k, v in sizes.items()},
        "pooled_quantile": pooled,
        "n_test_entries_pooled_fallback": missing,
    }


def false_trust(y: np.ndarray, event: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Per-state rate of ``T <= q`` over the draws (log scale, exact).

    ``y = ln min(T, H_max)`` and ``q`` (capped at ``ln H_max``) per (state,
    draw); a censored entry (``event`` false) never counts, because its
    ``T`` exceeds ``H_max >= q``.
    """
    return np.mean(event & (y <= q), axis=1)


# ------------------------------------------------------------ fit helpers
def subset_job(job: cb.FitJob, keep: np.ndarray, held: np.ndarray) -> cb.FitJob:
    """The job trained on states ``keep`` that predicts training states ``held``.

    A sample weight is renormalized to mean 1 on ``keep`` (M-2's
    ``kappa / mean_train(kappa)`` on the reduced training set).
    """
    weight = None
    if job.weight is not None:
        weight = job.weight[keep] / job.weight[keep].mean()
    return cb.FitJob(
        job.task,
        job.x_train[keep],
        job.y_train[keep],
        weight,
        job.domain[keep],
        job.order[keep],
        job.x_train[held],
        job.loss,
        {k: v[keep] for k, v in job.aux.items()},
        tau=job.tau,
        cap=job.cap,
    )


def cross_fit_jobs(
    job: cb.FitJob, n_folds: int
) -> list[tuple[np.ndarray, cb.FitJob]]:
    """One job per contiguous time block of the training states."""
    everything = np.arange(len(job.y_train))
    out = []
    for fold in cb.time_folds(job.order, n_folds):
        keep = np.setdiff1d(everything, fold)
        out.append((fold, subset_job(job, keep, fold)))
    return out


def assemble(
    folds: list[np.ndarray], preds: list[np.ndarray], n: int
) -> np.ndarray:
    """Out-of-fold predictions ``(n, r)`` from the per-block predictions."""
    out = np.full((n, preds[0].shape[1]), np.nan)
    for fold, pred in zip(folds, preds):
        out[fold] = pred
    return out


def _alloc_job(
    data: cb.SystemData,
    target: cb.Allocation,
    x_train: np.ndarray,
    x_test: np.ndarray,
) -> cb.FitJob:
    """The WU-0048 ``A/<set>`` job: u, weight ``kappa / mean kappa``."""
    return cb.FitJob(
        "regression",
        x_train,
        target.u,
        target.kappa / target.kappa.mean(),
        np.ones(len(target.u), bool),
        data.train["state_index"],
        x_test,
        "kappa_excess",
        {"kappa": target.kappa, "u": target.u, "w_star": target.w_star},
    )


def _quantile_job(
    data: cb.SystemData,
    y: np.ndarray,
    tau: float,
    x_train: np.ndarray,
    x_test: np.ndarray,
) -> cb.FitJob:
    """The WU-0048 ``Q<tau>/<set>`` job on target ``y`` (per state or row)."""
    return cb.FitJob(
        "quantile",
        x_train,
        y,
        None,
        np.ones(len(y), bool),
        data.train["state_index"],
        x_test,
        "pinball",
        {"y": y},
        tau=tau,
        cap=float(np.log(data.h_max)),
    )


def quantile_triplet(
    preds: list[np.ndarray], cap: float
) -> tuple[np.ndarray, int, int]:
    """Sort the three quantile predictions, cap them; count both."""
    ordered, crossed = cb.rearrange(np.stack(preds, axis=-1))
    return np.minimum(ordered, cap), crossed, int(np.sum(ordered > cap))


# --------------------------------------------------------------- readings
def retained_reading(
    row: dict, skill: dict, n_eff: tuple[float, ...] = ()
) -> str:
    """The C2 reading of a retained-skill row (module docstring)."""
    lower_skill = skill["ci"][0]
    if lower_skill is None or lower_skill <= 0:
        return "not determined (full-profile skill not established)"
    if any(not np.isfinite(v) or v < cb.MIN_EFFECTIVE for v in n_eff):
        return f"not determined (n_eff < {cb.MIN_EFFECTIVE})"
    lower, upper = row["ci"]
    if lower is None or upper is None:
        return "not determined (failed resamples)"
    if lower > RETAIN_LEVEL:
        return "keeps most"
    if upper < RETAIN_LEVEL:
        return "loses most"
    return "not determined (interval spans 0.5)"


def retained_rows(
    const: np.ndarray,
    bottleneck: np.ndarray,
    full: np.ndarray,
    index: np.ndarray,
    n_eff: tuple[float, ...] = (),
) -> dict:
    """Skill retained by a bottleneck, the full model's skill, and the reading.

    Per-state losses of the constant, the bottleneck and the full model.
    ``retained = mean(const - bottleneck) / mean(const - full)``; it is 1 for
    a bottleneck that equals the full model and 0 for one that equals the
    constant (identities, tested).
    """
    row = cb.ratio_row(
        const - bottleneck, const - full, index, cb.SHAPLEY_LEVEL, read=False
    )
    skill = cb.difference_row(const, full, index, cb.SHAPLEY_LEVEL)
    row["reading"] = retained_reading(row, skill, n_eff)
    return {"retained": row, "full_skill": skill}


def shapley_rank_rows(abd_system: dict) -> dict:
    """C2: Spearman's rho of the two decisions' Shapley shares (descriptive).

    Oracle profile; for each horizon the allocation ``phi`` (L_A) against the
    horizon ``phi`` (pinball). Four items: no interval, no test.
    """
    horizon = abd_system["horizon"]["oracle"]["shapley_pinball"]["rows"]
    phi_h = np.array([horizon[x]["phi"] for x in CONDITIONS])
    out = {}
    for hkey, blocks in abd_system["allocation"].items():
        rows = blocks["oracle"]["shapley_L_A"]["rows"]
        phi_a = np.array([rows[x]["phi"] for x in CONDITIONS])
        out[hkey] = {
            "horizon": blocks["oracle"]["horizon"],
            "spearman": spearman(phi_a, phi_h),
            "phi_allocation": dict(zip(CONDITIONS, phi_a.tolist())),
            "phi_horizon": dict(zip(CONDITIONS, phi_h.tolist())),
        }
    return out


C1_ALLOCATION: tuple[str, ...] = (
    "none",
    "A2 (stored)",
    "separation",
    "A4 (stored)",
    "A5 (stored)",
    "RO",
    "ROIN",
    "X",
    "A3 (stored)",
    "X+F",
)
C1_HORIZON: tuple[str, ...] = ("none", "lyapunov", "RO", "ROIN", "X", "X+F")


def c1_rows(abd_system: dict) -> dict:
    """C1: the A/D numbers of both decisions side by side (no refit).

    Allocation: MSE per rung and the ladder reading of each rung against F;
    horizon: pinball at 0.5, Harrell's C and the q_0.1 coverage per rung.
    """
    alloc = {}
    for hkey, blocks in abd_system["allocation"].items():
        for kind, b in blocks.items():
            lad = b["ladder"]
            alloc.setdefault(hkey, {})[kind] = {
                "horizon": b["horizon"],
                "mse": {
                    k: lad["mse"][k] for k in C1_ALLOCATION if k in lad["mse"]
                },
                "reading_vs_F": {
                    k: lad["vs_full"][k]["mse_ratio"].get("reading")
                    for k in C1_ALLOCATION
                    if k in lad["vs_full"]
                },
                "ratio_vs_F": {
                    k: lad["vs_full"][k]["mse_ratio"].get("ratio")
                    for k in C1_ALLOCATION
                    if k in lad["vs_full"]
                },
                "G_F": b["subsets"][FULL_KEY]["G"]["ratio"],
            }
    horizon = {}
    for kind, b in abd_system["horizon"].items():
        horizon[kind] = {
            k: {
                "pinball": b["rows"][k]["pinball_0.5"],
                "c_index": b["rows"][k]["c_index"]["c_index"],
                "coverage_0.1": b["rows"][k]["coverage"]["0.1"][
                    "coverage_below_cap"
                ],
                "reading_vs_F": (
                    b["ladder"]["vs_full"][k]["pinball_ratio"].get("reading")
                    if k in b["ladder"]["vs_full"]
                    else None
                ),
            }
            for k in C1_HORIZON
            if k in b["rows"]
        }
        horizon[kind]["lyapunov_rank_c"] = b["lyapunov_rank"]["c_index"]
    return {"allocation": alloc, "horizon": horizon}


# ------------------------------------------------------------- the system
Mapper = Callable[[Callable, Iterable], Iterable]


def _run(jobs: dict, learner: cb.Learner, mapper: Mapper) -> dict:
    keys = list(jobs)
    return dict(
        zip(keys, mapper(cb.run_job, [(jobs[k], learner) for k in keys]))
    )


def _with_cross_fit(
    jobs: dict, name: tuple, job: cb.FitJob, n_folds: int, folds_out: dict
) -> None:
    jobs[(*name, "full")] = job
    parts = cross_fit_jobs(job, n_folds)
    folds_out[name] = [fold for fold, _ in parts]
    for k, (_, sub) in enumerate(parts):
        jobs[(*name, k)] = sub


def _oof(results: dict, name: tuple, folds: dict, n: int) -> np.ndarray:
    preds = [results[(*name, k)].pred for k in range(len(folds[name]))]
    return assemble(folds[name], preds, n)


def analyze_joint(
    data: cb.SystemData,
    arrays: dict[str, np.ndarray],
    learner: cb.Learner,
    index: np.ndarray,
    *,
    mapper: Mapper = map,
) -> dict:
    """C2 and C3 for one system of one run (see the module docstring).

    Parameters
    ----------
    data : SystemData
        The system's dump (``contribution.SystemData``).
    arrays : dict[str, np.ndarray]
        The raw dump (full-grid per-draw errors, verification noise, leaves,
        the calibration split).
    learner : Learner
        The WU-0048 learner (``contribution.Learner`` with the run's master
        seed and ``GRID``), so every fit is the one WU-0048 would make.
    index : np.ndarray
        The shared moving-block index sets ``(B, n_test)`` of the system
        (``contribution.resample_indices`` of
        ``contribution.bootstrap_generator``, as in WU-0048).
    mapper : callable, optional
        ``map``-like executor of ``contribution.run_job``.

    Returns
    -------
    dict
        ``label``, ``checks``, ``C2`` and ``C3``.
    """
    n_folds = learner.n_folds
    cap = float(np.log(data.h_max))
    lt = data.steps_per_lt
    cols = data.horizons - 1
    tr_cross = cb.crossing_time(
        data.train["E_C"],
        data.train["E_P"],
        data.train["C"],
        data.noise,
        data.theta,
    )
    te_cross = cb.crossing_time(
        data.test["E_C"],
        data.test["E_P"],
        data.test["C"],
        data.noise,
        data.theta,
    )
    n_tr, n_te = len(tr_cross.y), len(te_cross.y)
    targets = {
        c: (
            cb.allocation_targets(
                *(data.train[k][:, h] for k in ("E_C", "E_P", "C"))
            ),
            cb.allocation_targets(
                *(data.test[k][:, h] for k in ("E_C", "E_P", "C"))
            ),
        )
        for c, h in enumerate(cols)
    }
    oracle_tr = cb.profile_inputs(data, "oracle", "train")
    oracle_te = cb.profile_inputs(data, "oracle", "test")
    dep_tr = cb.profile_inputs(data, "deployable", "train")
    dep_te = cb.profile_inputs(data, "deployable", "test")

    # A2 on 1..H_max from the construction moments, checked against the dump.
    con = "split/construction"
    con_moments = tuple(arrays[f"{con}/{k}"] for k in ("E_C", "E_P", "C"))
    a2_full = pooled_weight(*con_moments)
    a2_counts = {
        "pooled_curvature_floor": int(
            np.sum(
                np.sum(con_moments[0] + con_moments[1] - 2 * con_moments[2], 0)
                < cb.CURVATURE_FLOOR
            )
        ),
        "columns_at_0_or_1": int(np.sum((a2_full == 0.0) | (a2_full == 1.0))),
    }
    a2_dumped = data.test["a2_weight"]
    if not np.array_equal(
        np.broadcast_to(a2_full[cols], a2_dumped.shape), a2_dumped
    ):
        raise ValueError(
            "A2 rebuilt on 1..H_max differs from split/test/a2_weight"
        )
    a4_dumped = data.test["a4_weight"]
    if not np.all(a4_dumped == a4_dumped[:, :, :1]):
        raise ValueError("the stored A4 weight depends on the horizon")
    a2_train = policy_crossing(
        data.train["E_C"],
        data.train["E_P"],
        data.train["C"],
        a2_full,
        data.noise,
        data.theta,
    )

    # Stage 1: g(F), h(F) oracle (cross-fitted); g(F-hat) cross-fitted; h_A2.
    jobs: dict = {}
    folds: dict = {}
    for c in range(len(cols)):
        tr, _ = targets[c]
        _with_cross_fit(
            jobs,
            ("g", "oracle", c),
            _alloc_job(data, tr, oracle_tr, oracle_te),
            n_folds,
            folds,
        )
        _with_cross_fit(
            jobs,
            ("g", "deployable", c),
            _alloc_job(data, tr, dep_tr, dep_te),
            n_folds,
            folds,
        )
    for tau in cb.TAUS:
        _with_cross_fit(
            jobs,
            ("h", "oracle", tau),
            _quantile_job(data, tr_cross.y, tau, oracle_tr, oracle_te),
            n_folds,
            folds,
        )
        jobs[("hA2", tau)] = _quantile_job(
            data, a2_train.y[:, 0], tau, dep_tr, dep_te
        )
    res1 = _run(jobs, learner, mapper)

    g_oracle_te = np.concatenate(
        [
            np.clip(res1[("g", "oracle", c, "full")].pred, 0, 1)
            for c in range(len(cols))
        ],
        axis=1,
    )[:, None, :]
    g_oracle_tr = np.concatenate(
        [
            np.clip(_oof(res1, ("g", "oracle", c), folds, n_tr), 0, 1)
            for c in range(len(cols))
        ],
        axis=1,
    )[:, None, :]
    h_te, h_te_crossed, h_te_capped = quantile_triplet(
        [res1[("h", "oracle", tau, "full")].pred for tau in cb.TAUS], cap
    )
    h_tr, h_tr_crossed, h_tr_capped = quantile_triplet(
        [_oof(res1, ("h", "oracle", tau), folds, n_tr) for tau in cb.TAUS], cap
    )
    g_dep_te_raw = np.stack(
        [res1[("g", "deployable", c, "full")].pred for c in range(len(cols))],
        axis=-1,
    )
    g_dep_tr_raw = np.stack(
        [
            _oof(res1, ("g", "deployable", c), folds, n_tr)
            for c in range(len(cols))
        ],
        axis=-1,
    )

    def outside(x: np.ndarray) -> int:
        return int(np.sum((x < 0.0) | (x > 1.0)))

    g_oracle_raw = [
        res1[("g", "oracle", c, "full")].pred for c in range(len(cols))
    ]
    clipped = {
        "g_oracle_test": sum(outside(p) for p in g_oracle_raw),
        "g_oracle_train_oof": sum(
            outside(_oof(res1, ("g", "oracle", c), folds, n_tr))
            for c in range(len(cols))
        ),
        "g_deployable_test": outside(g_dep_te_raw),
        "g_deployable_train_oof": outside(g_dep_tr_raw),
    }
    g_dep_te = np.clip(g_dep_te_raw, 0.0, 1.0)
    g_dep_tr = np.clip(g_dep_tr_raw, 0.0, 1.0)
    g_full_tr = full_grid_weight(g_dep_tr, data.horizons, data.h_max)
    g_train = policy_crossing(
        data.train["E_C"],
        data.train["E_P"],
        data.train["C"],
        g_full_tr,
        data.noise,
        data.theta,
    )

    # Stage 2: the bottlenecks and h(F-hat) of the full system.
    jobs2: dict = {}
    for tau in cb.TAUS:
        jobs2[("fwd", tau)] = _quantile_job(
            data, tr_cross.y, tau, g_oracle_tr, g_oracle_te
        )
        jobs2[("hg", tau)] = _quantile_job(data, g_train.y, tau, dep_tr, dep_te)
    for c in range(len(cols)):
        jobs2[("fwd1", c)] = _quantile_job(
            data,
            tr_cross.y,
            0.5,
            g_oracle_tr[..., c : c + 1],
            g_oracle_te[..., c : c + 1],
        )
        jobs2[("rev", c)] = _alloc_job(data, targets[c][0], h_tr, h_te)
    res2 = _run(jobs2, learner, mapper)

    # ---- C2 forward
    const_q = np.quantile(tr_cross.y, cb.TAUS)
    pin_const = cb.pinball(te_cross.y, np.full((n_te, 1), const_q[1]), 0.5)
    pin_full = cb.pinball(te_cross.y, h_te[..., 1], 0.5)
    fwd, fwd_crossed, fwd_capped = quantile_triplet(
        [res2[("fwd", tau)].pred for tau in cb.TAUS], cap
    )
    pin_fwd = cb.pinball(te_cross.y, fwd[..., 1], 0.5)
    time = np.minimum(te_cross.T_c, data.h_max)
    forward = {
        "target": "Y = ln min(T_c, H_max), oracle hybrid (the WU-0048 horizon target)",
        "inputs": "g(F): clipped allocation outputs at the five evaluation horizons",
        "pinball": {
            "constant": float(pin_const.mean()),
            "F": float(pin_full.mean()),
            "g(F)": float(pin_fwd.mean()),
        },
        "c_index": {
            "F": cb.harrell_c(time, te_cross.event, h_te[..., 1])[0],
            "g(F)": cb.harrell_c(time, te_cross.event, fwd[..., 1])[0],
        },
        "pinball_ratio_bottleneck_over_F": cb.ratio_row(
            pin_fwd, pin_full, index, cb.SHAPLEY_LEVEL
        ),
        **retained_rows(pin_const, pin_fwd, pin_full, index),
        "single_horizon": {},
        "n_crossed": fwd_crossed,
        "n_capped": fwd_capped,
        "settings": {f"{tau:g}": res2[("fwd", tau)].setting for tau in cb.TAUS},
    }
    for c, h in enumerate(data.horizons):
        raw = res2[("fwd1", c)].pred
        pin = cb.pinball(te_cross.y, np.minimum(raw, cap), 0.5)
        rows = retained_rows(pin_const, pin, pin_full, index)
        forward["single_horizon"][str(int(h))] = {
            "horizon": data.horizon_label(int(h)),
            "pinball": float(pin.mean()),
            "retained": rows["retained"],
            "n_capped": int(np.sum(raw > cap)),
        }

    # ---- C2 reverse
    reverse = {}
    for c, h in enumerate(data.horizons):
        tr, te = targets[c]
        moments = tuple(
            data.test[k][:, int(h) - 1] for k in ("E_C", "E_P", "C")
        )
        const = cb.score_allocation(
            np.full((n_te, 1), cb.kappa_baseline(tr.kappa, tr.u)),
            te,
            moments,
            None,
        )
        full = cb.score_allocation(
            res1[("g", "oracle", c, "full")].pred, te, moments, None
        )
        bott = cb.score_allocation(res2[("rev", c)].pred, te, moments, None)
        n_eff = cb.guard_sizes(te.kappa, full.excess)
        rows = retained_rows(const.mse, bott.mse, full.mse, index, n_eff)
        reverse[str(int(h))] = {
            "horizon": data.horizon_label(int(h)),
            "inputs": "h(F): the three horizon quantile outputs (log steps)",
            "mse": {
                "constant": float(const.mse.mean()),
                "F": float(full.mse.mean()),
                "h(F)": float(bott.mse.mean()),
            },
            "n_eff": list(n_eff),
            "mse_ratio_bottleneck_over_F": cb.ratio_row(
                bott.mse, full.mse, index, cb.SHAPLEY_LEVEL, n_eff=n_eff
            ),
            **rows,
            "n_pred_clipped": bott.n_clipped,
            "setting": res2[("rev", c)].setting,
        }

    c2 = {
        "profile": "oracle",
        "forward": forward,
        "reverse": reverse,
        "counts": {
            "h_test_crossed": h_te_crossed,
            "h_test_capped": h_te_capped,
            "h_train_oof_crossed": h_tr_crossed,
            "h_train_oof_capped": h_tr_capped,
        },
        "prediction_check": c2_prediction(forward, reverse),
    }

    # ---- C3
    t = data.test
    cp_full, plp_full, vnoise = (
        arrays[f"split/test/{k}"]
        for k in ("cp_err_full", "plp_err_full", "verify_noise")
    )
    n_draws = cp_full.shape[1]
    a4_w = a4_dumped[:, :, :1]
    hA2, hA2_crossed, hA2_capped = quantile_triplet(
        [res1[("hA2", tau)].pred for tau in cb.TAUS], cap
    )
    hg, hg_crossed, hg_capped = quantile_triplet(
        [res2[("hg", tau)].pred for tau in cb.TAUS], cap
    )
    a2_const_q = np.minimum(np.quantile(a2_train.y[:, 0], cb.TAUS), cap)

    # A4 + KM leaf: calibration A4 hybrid's characteristic horizon per pair.
    cal = "split/calibration"
    cal_profile = arrays[f"{cal}/profile_deployable"]
    a4_cal = cb.separation_weight(cal_profile)  # the A4 formula (WU-0048 check)
    cal_cross = policy_crossing(
        arrays[f"{cal}/E_C"],
        arrays[f"{cal}/E_P"],
        arrays[f"{cal}/C"],
        np.repeat(a4_cal[:, :, None], data.h_max, axis=2),
        data.noise,
        data.theta,
    )
    leaf_q, leaf_record = leaf_quantiles(
        arrays["core/a5_leaf_calibration"],
        cal_cross.T,
        cal_cross.event,
        arrays["core/a5_leaf"],
        data.h_max,
    )

    g_full_te = full_grid_weight(g_dep_te, data.horizons, data.h_max)
    policies = {
        "A2 + constant": (
            np.broadcast_to(a2_full[cols], (n_te, n_draws, len(cols))),
            np.broadcast_to(a2_full, cp_full.shape),
            np.full((n_te, n_draws), a2_const_q[0]),
        ),
        "A2 + h(F-hat)": (
            np.broadcast_to(a2_full[cols], (n_te, n_draws, len(cols))),
            np.broadcast_to(a2_full, cp_full.shape),
            hA2[..., 0],
        ),
        "A4 + KM leaf": (
            np.broadcast_to(a4_w, (n_te, n_draws, len(cols))),
            np.broadcast_to(a4_w, cp_full.shape),
            np.minimum(np.log(leaf_q), cap),
        ),
        "g(F-hat) + h(F-hat)": (g_dep_te, g_full_te, hg[..., 0]),
    }
    per_state: dict[str, dict[str, np.ndarray]] = {}
    mse_scores: dict[str, list] = {}
    for name, (w5, wfull, q01) in policies.items():
        dur, ev = realized_policy_horizon(
            wfull, cp_full, plp_full, vnoise, data.theta
        )
        char = policy_crossing(
            t["E_C"], t["E_P"], t["C"], wfull, data.noise, data.theta
        )
        per_state[name] = {
            "false_trust_realized": false_trust(np.log(dur), ev, q01),
            "false_trust_characteristic": false_trust(char.y, char.event, q01),
            "trusted_lt": np.mean(np.exp(q01), axis=1) / lt,
            "n_q_at_cap": int(np.sum(q01 >= cap)),
            "share_realized_censored": float(np.mean(~ev)),
            "share_characteristic_censored": float(np.mean(~char.event)),
        }
        scores = []
        for c, h in enumerate(data.horizons):
            _, te = targets[c]
            moments = tuple(t[k][:, int(h) - 1] for k in ("E_C", "E_P", "C"))
            errors = (t["cp_err"][:, :, c], t["plp_err"][:, :, c])
            scores.append(
                cb.score_allocation(
                    np.ascontiguousarray(w5[..., c]), te, moments, errors
                )
            )
        mse_scores[name] = scores

    c3_rows = {}
    ref_name = "A2 + constant"
    for name in policies:
        ps = per_state[name]
        mse = {}
        for c, h in enumerate(data.horizons):
            _, te = targets[c]
            sc, ref = mse_scores[name][c], mse_scores[ref_name][c]
            mse[str(int(h))] = {
                "horizon": data.horizon_label(int(h)),
                "mse": float(sc.mse.mean()),
                "ratio_to_A2": cb.ratio_row(
                    sc.mse,
                    ref.mse,
                    index,
                    cb.SHAPLEY_LEVEL,
                    n_eff=cb.guard_sizes(te.kappa, ref.subst - te.v_star),
                ),
                "n_pred_clipped": sc.n_clipped,
            }
        c3_rows[name] = {
            "mse": mse,
            "false_trust_realized": cb.estimate_row(
                ps["false_trust_realized"], index
            ),
            "false_trust_characteristic": cb.estimate_row(
                ps["false_trust_characteristic"], index
            ),
            "mean_trusted_lt": cb.estimate_row(ps["trusted_lt"], index),
            "n_q_at_cap": ps["n_q_at_cap"],
            "share_realized_censored": ps["share_realized_censored"],
            "share_characteristic_censored": ps[
                "share_characteristic_censored"
            ],
        }
    full_name = "g(F-hat) + h(F-hat)"
    contrasts = {}
    for name in policies:
        if name == full_name:
            continue
        contrasts[name] = {
            key: cb.estimate_row(
                per_state[full_name][key] - per_state[name][key], index
            )
            for key in (
                "false_trust_realized",
                "false_trust_characteristic",
                "trusted_lt",
            )
        }

    # quality of the two horizon models on their own (characteristic) targets
    a2_test = policy_crossing(
        t["E_C"], t["E_P"], t["C"], a2_full, data.noise, data.theta
    )
    g_test = policy_crossing(
        t["E_C"], t["E_P"], t["C"], g_full_te, data.noise, data.theta
    )
    g_const_q = np.quantile(g_train.y, cb.TAUS)
    horizon_models = {}
    for name, y_te, ev_te, pred, const_qs, (crossed, capped) in (
        (
            "h_A2(F-hat)",
            a2_test.y[:, 0],
            a2_test.event[:, 0],
            hA2,
            a2_const_q,
            (hA2_crossed, hA2_capped),
        ),
        (
            "h_g(F-hat)",
            g_test.y,
            g_test.event,
            hg,
            np.minimum(g_const_q, cap),
            (hg_crossed, hg_capped),
        ),
    ):
        pin_m = cb.pinball(y_te, pred[..., 1], 0.5)
        pin_c = cb.pinball(y_te, np.full(pred.shape[:2], const_qs[1]), 0.5)
        record = {
            "pinball": float(pin_m.mean()),
            "pinball_constant": float(pin_c.mean()),
            "pinball_ratio_constant_over_model": cb.ratio_row(
                pin_c, pin_m, index, cb.SHAPLEY_LEVEL
            ),
            "coverage": {
                f"{tau:g}": cb.coverage(y_te, ev_te, pred[..., i], cap)
                for i, tau in enumerate(cb.TAUS)
            },
            "n_crossed": crossed,
            "n_capped": capped,
        }
        if y_te.ndim == 1:
            record["c_index"] = cb.harrell_c(
                np.minimum(a2_test.T_c[:, 0], data.h_max), ev_te, pred[..., 1]
            )[0]
        horizon_models[name] = record

    # Reproduction of WU-0048's A/ROIN predictions: the same job, the same fit.
    checks = {
        "a2_full_grid_equals_dump": True,
        "a2_full_grid_counts": a2_counts,
        "a4_horizon_free": True,
        "crossing_counts": {
            "a2_train": [a2_train.n_first_step, a2_train.n_exact_theta],
            "g_train": [g_train.n_first_step, g_train.n_exact_theta],
            "a2_test": [a2_test.n_first_step, a2_test.n_exact_theta],
            "g_test": [g_test.n_first_step, g_test.n_exact_theta],
            "calibration_a4": [cal_cross.n_first_step, cal_cross.n_exact_theta],
        },
        "g_mse": {
            kind: {
                str(int(h)): float(
                    cb.score_allocation(
                        res1[("g", kind, c, "full")].pred,
                        targets[c][1],
                        tuple(t[k][:, int(h) - 1] for k in ("E_C", "E_P", "C")),
                        (
                            None
                            if kind == "oracle"
                            else (t["cp_err"][:, :, c], t["plp_err"][:, :, c])
                        ),
                    ).mse.mean()
                )
                for c, h in enumerate(data.horizons)
            }
            for kind in ("oracle", "deployable")
        },
        "n_pred_clipped": clipped,
        "settings": {
            f"g/{kind}/{int(h)}": res1[("g", kind, c, "full")].setting
            for kind in ("oracle", "deployable")
            for c, h in enumerate(data.horizons)
        },
    }
    c3 = {
        "profile": "deployable",
        "policies": c3_rows,
        "full_minus_comparator": contrasts,
        "horizon_models": horizon_models,
        "km_leaf": leaf_record,
        "notes": [
            "A4 + KM leaf: characteristic horizon of the calibration A4 hybrid "
            "per pair (the dump has no per-draw calibration errors on 1..H_max)",
            "g(F-hat) on 1..H_max: linear in ln H between the five horizons, "
            "constant beyond them",
            "false trust: q_0.1 capped at H_max; censored paths never count",
        ],
    }
    return {
        "label": cb.LABEL.format(seed_id=data.seed_id),
        "system": data.system,
        "checks": checks,
        "C2": c2,
        "C3": c3,
    }


def c2_prediction(forward: dict, reverse: dict) -> dict:
    """The math spec's C2 prediction against the readings (descriptive).

    The prediction: both bottlenecks lose most of their skill. "consistent"
    if the forward reading and every determined reverse reading are "loses
    most" (at least one determined); "not consistent" if any reads "keeps
    most"; otherwise "not determined".
    """
    readings = [forward["retained"]["reading"]] + [
        r["retained"]["reading"] for r in reverse.values()
    ]
    determined = [r for r in readings if r in ("keeps most", "loses most")]
    if "keeps most" in determined:
        text = "not consistent"
    elif determined and forward["retained"]["reading"] == "loses most":
        text = "consistent"
    else:
        text = "not determined"
    single = {
        h: r["retained"]["ratio"] for h, r in forward["single_horizon"].items()
    }
    return {
        "reading": text,
        "forward_single_horizon_retained": single,
        "forward_single_largest_at": (
            max(
                (h for h in single if single[h] is not None),
                key=lambda h: single[h],
                default=None,
            )
        ),
    }
