"""LPC contribution study, experiments A, B and D (phase J, WU-0048).

DEVELOPMENT, exploratory: every number this module produces is an estimate on
a development seed, read by tables, never passed or failed. It runs offline on
the opt-in state dump of schema /3 (``lpcstudy.dump``, the ``split/`` group)
and never touches a forecasting run.

Governing documents: the phase J plan
(``docs/agent/notes/2026-10-26-phase-j-lpc-contribution-plan.md``) and the
mathematics specification (``...-phase-j-math-spec.md``, M-1 to M-8), which
governs where they differ, plus the main session's design decisions of
2026-10-26 after the WU-0048a quick look (inner cross-validation of the
learner's complexity, Kish effective size of the curvature, readings on the
MSE ratio, the separation formula as a reference column, logit scale for B,
horizons labeled by steps and Lyapunov times).

The two decisions
    *Allocation* at each evaluation horizon ``H`` (one fit per horizon, M-1).
    With ``kappa = E_C + E_P - 2C`` and ``u = (E_P - C) / kappa``, the
    expected squared error of weight ``w`` is ``V(w) = kappa (w - u)^2 +
    V(u)``, so the excess over ``w* = clip(u, 0, 1)`` is ``kappa [(w - u)^2 -
    (w* - u)^2]`` (:func:`excess_kappa`). A learned rule fits ``u`` with sample
    weight ``kappa / mean_train(kappa)`` (M-2) and its predictions are clipped
    to ``[0, 1]`` and counted. The second loss ``L_w`` (``kappa = 1``, fitted
    with unit weights) is reported beside it. Oracle-profile rows are scored
    by the moment form; deployable-profile rows by the realized per-draw score
    ``S_i = mean_j (g_ij e_C + (1 - g_ij) e_P)^2`` (M-8,
    :func:`realized_score`), with the V-substituted value and its dependence
    bias (test (f2)) beside it.

    *Horizon*: the oracle hybrid's crossing time ``T_c`` at ``theta``
    (log-linear interpolation, ``ceil(T_c) = T``, M-4), predicted on ``Y = ln
    min(T_c, H_max)`` by quantile boosting at 0.1, 0.5 and 0.9. Scores: pinball
    loss, Harrell's C (M-4 tie rules), coverage below the cap with the
    all-state bracket.

The learner
    ``HistGradientBoosting`` with the Q-N hyperparameters as one setting of a
    small grid fixed in advance (``GRID``). The setting of every model is
    chosen by inner blocked cross-validation on the training states only (five
    contiguous blocks in time order), with the model's own decision loss; ties
    go to the more regularized setting. ``min_samples_leaf`` counts states: a
    deployable model, trained on one row per (state, draw), uses ``E`` times
    as many rows, and each row carries ``1/E`` of its state's weight. The
    empty subset is the closed-form constant (A2 refit on the training rows,
    test (a')).

Uncertainty and readings
    One paired moving-block bootstrap per system (blocks of 5, ``B``
    resamples) over the test states in time order, with every model held fixed
    and one index set shared by every row, decision, profile and horizon of the
    system. A non-finite resample is failed and counted (M-7). Allocation rows
    are read on the MSE ratio ``MSE(simpler) / MSE(richer)`` by
    ``ablation.ratio_reading`` (margin 1.05); the excess-loss ratio and the
    gain share ``G`` are estimates without a reading. A ratio reads
    "undetermined (n_eff < 50)" when the Kish effective size of ``kappa`` on
    the test states, or the effective size of the reference rule's per-state
    excess, is below 50. Families (Holm on bootstrap p-values, intervals at
    ``1 - 0.05/m``): A's four drop-one rows, B's six pairs, D's rungs against
    the full profile. Shapley shares and the reference columns are 95%
    estimates. The theory gap is an upper bound (M-2 rule 3).

Randomness: the bootstrap indices come from ``make_rng(seed, system,
"bootstrap", "phase-J-contrib")``; the scikit-learn seed is
``sklearn_seed(seed, "phase-j-learner")``. No other random number is drawn
(folds and the interaction sample are deterministic).

Handled cases are counted, never silent: curvature below the ``1e-300``
floor, predictions clipped to ``[0, 1]``, quantile crossings and caps,
``T = 1`` and ``e_{T-1} = theta`` in ``T_c``, single-class training sets,
failed cross-validation folds, undefined Lyapunov forms, failed resamples.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
from scipy.special import expit
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)

from .ablation import (
    CONDITIONS,
    SUBSETS,
    ratio_reading_reason,
    shapley_weight,
    subset_key,
)
from .data import make_rng, sklearn_seed
from .statistics import (
    MIN_STATES,
    block_resample_indices,
    endpoint_mc_error,
    holm_adjust,
    percentile_interval,
)

LABEL: str = "DEVELOPMENT ({seed_id}): exploratory, not a hypothesis test"
"""The label of every table and record (plan section 3.4)."""
TAUS: tuple[float, float, float] = (0.1, 0.5, 0.9)
"""Quantile levels of the horizon models (DS-4)."""
N_FOLDS: int = 5
"""Inner cross-validation folds (contiguous blocks in time order)."""
MIN_EFFECTIVE: int = MIN_STATES
"""Effective-size guard of the ratio readings (math spec M-2 rule 1)."""
CURVATURE_FLOOR: float = 1e-300
"""The floor of ``oracle.oracle_weight``; a curvature below it is counted."""
INDICATOR_SHARE: float = 0.05
"""The ``w* = 1`` part of B is fitted where its test share exceeds this."""
INTERACTION_SAMPLE: int = 200
"""Test states (evenly spaced) of Friedman's H^2 (descriptive)."""
LATENT_DIM: int = 3
"""``m`` of the Lyapunov horizon form (the three core systems are 3-D)."""
SHAPLEY_LEVEL: float = 0.95
"""Level of the Shapley rows and the reference columns (estimates)."""
PAIRS: tuple[tuple[int, int], ...] = tuple(combinations(range(4), 2))
"""The six condition pairs of B."""
PRIMARY_PAIRS: tuple[str, str] = ("RI", "OI")
"""The pairs named primary in advance (plan section 3.4)."""
FULL: tuple[int, ...] = SUBSETS[-1]
"""The full profile ``(0, 1, 2, 3)``."""
INTERIOR_LIMIT: float = 1.0
"""``u`` at or above this is the ``w* = 1`` part (``u <= 0``: ``w* = 0``)."""


# ------------------------------------------------------------------ learner
@dataclass(frozen=True)
class Setting:
    """One complexity setting of the learner (``min_leaf_states`` in states)."""

    name: str
    max_iter: int
    learning_rate: float
    max_leaf_nodes: int
    min_leaf_states: int
    l2: float


GRID: tuple[Setting, ...] = (
    Setting("qn", 300, 0.05, 15, 20, 1.0),
    Setting("mid", 100, 0.05, 8, 100, 1.0),
    Setting("low", 50, 0.05, 4, 200, 1.0),
)
"""The grid, least to most regularized; ``qn`` is ``analysis.qn_regressor``.

Fixed before any phase J data were read (main session, 2026-10-26)."""


@dataclass(frozen=True)
class Learner:
    """The learner: master seed, the grid and the number of folds.

    A grid of one setting skips the cross-validation.
    """

    seed: int
    grid: tuple[Setting, ...] = GRID
    n_folds: int = N_FOLDS


def make_estimator(
    task: str,
    setting: Setting,
    seed: int,
    rows_per_state: int,
    tau: float | None = None,
    cst: list[list[int]] | None = None,
):
    """Return an unfitted estimator of ``task`` at ``setting``.

    ``task`` is ``"regression"`` (squared loss), ``"quantile"`` (pinball at
    ``tau``) or ``"classifier"`` (log loss). ``early_stopping`` is off, as in
    Q-N, so the fit draws no random number.
    """
    common = dict(
        max_iter=setting.max_iter,
        learning_rate=setting.learning_rate,
        max_leaf_nodes=setting.max_leaf_nodes,
        min_samples_leaf=setting.min_leaf_states * rows_per_state,
        l2_regularization=setting.l2,
        early_stopping=False,
        interaction_cst=cst,
        random_state=sklearn_seed(seed, "phase-j-learner"),
    )
    if task == "regression":
        return HistGradientBoostingRegressor(**common)
    if task == "quantile":
        return HistGradientBoostingRegressor(
            loss="quantile", quantile=tau, **common
        )
    if task == "classifier":
        return HistGradientBoostingClassifier(**common)
    raise ValueError(f"unknown task {task!r}")


@dataclass
class FitJob:
    """One model: training data, test inputs, loss and constraints.

    Arrays are per state; inputs are ``(n, r, p)`` with ``r`` rows per state
    (1 for the oracle profile, ``E`` draws for the deployable one).

    Attributes
    ----------
    task : str
        ``regression``, ``quantile`` or ``classifier``.
    x_train, x_test : np.ndarray
        Inputs ``(n_tr, r, p)`` and ``(n_te, r', p)``.
    y_train : np.ndarray
        Target per training state ``(n_tr,)``.
    weight : np.ndarray or None
        Sample weight per training state (already normalized), or None.
    domain : np.ndarray
        Training states in the target's domain (bool ``(n_tr,)``).
    order : np.ndarray
        Time index of each training state (for the folds).
    loss : str
        The decision loss of :func:`state_loss` used for the selection.
    aux : dict[str, np.ndarray]
        Per-training-state arrays of the loss.
    tau : float or None
        Quantile level.
    cap : float or None
        Predictions above it are capped (horizon models; counted at test).
    cst : list or None
        ``interaction_cst``.
    h2_sample : np.ndarray or None
        If given, ``(m, p)`` points for Friedman's H^2 of the final model.
    """

    task: str
    x_train: np.ndarray
    y_train: np.ndarray
    weight: np.ndarray | None
    domain: np.ndarray
    order: np.ndarray
    x_test: np.ndarray
    loss: str
    aux: dict[str, np.ndarray]
    tau: float | None = None
    cap: float | None = None
    cst: list[list[int]] | None = None
    h2_sample: np.ndarray | None = None


@dataclass
class FitResult:
    """Test predictions ``(n_te, r')`` of a job and its selection record.

    ``pred`` is NaN if the final fit failed (a single class), counted in
    ``failed``. ``cv_loss`` maps each setting to its mean fold loss (NaN if
    every fold failed); ``n_fold_failed`` counts the failed (setting, fold)
    fits.
    """

    pred: np.ndarray
    setting: str
    cv_loss: dict[str, float]
    n_fold_failed: int
    failed: bool
    h2: dict[str, float] = field(default_factory=dict)


def time_folds(order: np.ndarray, n_folds: int) -> list[np.ndarray]:
    """Split positions into ``n_folds`` contiguous blocks in time order."""
    ranked = np.argsort(order, kind="stable")
    return [b for b in np.array_split(ranked, n_folds) if b.size]


def _flatten(x: np.ndarray) -> np.ndarray:
    return x.reshape(-1, x.shape[-1])


def _fit(job: FitJob, setting: Setting, learner: Learner, rows: np.ndarray):
    """Fit on the training states ``rows``; None if the target is one class."""
    r = job.x_train.shape[1]
    y = np.repeat(job.y_train[rows], r)
    if job.task == "classifier" and np.unique(y).size < 2:
        return None
    weight = None
    if job.weight is not None:
        weight = np.repeat(job.weight[rows] / r, r)
    elif r > 1:
        weight = np.full(y.size, 1.0 / r)
    model = make_estimator(job.task, setting, learner.seed, r, job.tau, job.cst)
    return model.fit(_flatten(job.x_train[rows]), y, sample_weight=weight)


def predict_rows(model, task: str, x: np.ndarray) -> np.ndarray:
    """Predictions ``(n, r)`` for inputs ``(n, r, p)``.

    A classifier returns its raw log-odds (``decision_function``), so the log
    loss needs no clipping of probabilities.
    """
    flat = _flatten(x)
    out = (
        model.decision_function(flat)
        if task == "classifier"
        else model.predict(flat)
    )
    return np.asarray(out, dtype=float).reshape(x.shape[0], x.shape[1])


def state_loss(
    kind: str,
    pred: np.ndarray,
    aux: dict[str, np.ndarray],
    tau: float | None = None,
) -> np.ndarray:
    """Per-state decision loss of predictions ``(n, r)``, averaged over rows.

    ``kind``:

    * ``kappa_excess``: ``kappa [(clip(g) - u)^2 - (w* - u)^2]`` (aux
      ``kappa``, ``u``, ``w_star``), the moment form of ``L_A``;
    * ``unit_excess``: the same with ``kappa = 1`` (``L_w``);
    * ``squared``: ``(g - y)^2``;
    * ``log_loss``: ``ln(1 + e^g) - y g`` for raw log-odds ``g``;
    * ``pinball``: ``max(tau (y - g), (tau - 1)(y - g))``.
    """
    if kind in ("kappa_excess", "unit_excess"):
        g = np.clip(pred, 0.0, 1.0)
        kappa = aux["kappa"][:, None] if kind == "kappa_excess" else 1.0
        u, ws = aux["u"][:, None], aux["w_star"][:, None]
        return np.mean(kappa * ((g - u) ** 2 - (ws - u) ** 2), axis=1)
    y = aux["y"][:, None]
    if kind == "squared":
        return np.mean((pred - y) ** 2, axis=1)
    if kind == "log_loss":
        return np.mean(np.logaddexp(0.0, pred) - y * pred, axis=1)
    if kind == "pinball":
        diff = y - pred
        return np.mean(np.maximum(tau * diff, (tau - 1.0) * diff), axis=1)
    raise ValueError(f"unknown loss {kind!r}")


def _capped(job: FitJob, pred: np.ndarray) -> np.ndarray:
    return pred if job.cap is None else np.minimum(pred, job.cap)


def select_setting(
    job: FitJob, learner: Learner
) -> tuple[Setting, dict[str, float], int]:
    """Choose the setting by blocked cross-validation on the training states.

    Only ``job.x_train``, ``job.y_train``, ``job.weight``, ``job.aux`` and
    ``job.order`` are read: the test inputs never enter the choice. The fold
    loss is the job's decision loss, averaged over the fold's states; a
    setting's score is the state-weighted mean over its successful folds.
    Ties go to the later (more regularized) setting.

    Returns
    -------
    tuple
        The setting, the score of every setting, and the failed fits.
    """
    if len(learner.grid) == 1:
        return learner.grid[0], {learner.grid[0].name: float("nan")}, 0
    states = np.flatnonzero(job.domain)
    folds = time_folds(job.order[states], learner.n_folds)
    scores: dict[str, float] = {}
    n_failed = 0
    for setting in learner.grid:
        total, count = 0.0, 0
        for fold in folds:
            held = states[fold]
            kept = np.setdiff1d(states, held)
            model = _fit(job, setting, learner, kept)
            if model is None:
                n_failed += 1
                continue
            pred = _capped(
                job, predict_rows(model, job.task, job.x_train[held])
            )
            aux = {k: v[held] for k, v in job.aux.items()}
            total += float(np.sum(state_loss(job.loss, pred, aux, job.tau)))
            count += held.size
        scores[setting.name] = total / count if count else float("nan")
    finite = [(v, i) for i, v in enumerate(scores.values()) if np.isfinite(v)]
    if not finite:
        return learner.grid[0], scores, n_failed
    best = min(v for v, _ in finite)
    chosen = max(i for v, i in finite if v == best)
    return learner.grid[chosen], scores, n_failed


def friedman_h2(model, task: str, x: np.ndarray) -> dict[str, float]:
    """Friedman's H^2 of every pair of the first four inputs (descriptive).

    Partial dependences are evaluated at the rows of ``x`` ``(m, p)`` and
    centered; ``H^2_jk = sum (PD_jk - PD_j - PD_k)^2 / sum PD_jk^2``. NaN if
    the pair's partial dependence is identically 0.
    """
    m = len(x)

    def pd(cols: tuple[int, ...]) -> np.ndarray:
        grid = np.repeat(x[None, :, :], m, axis=0)  # grid[i, l] = x_l
        for c in cols:
            grid[:, :, c] = x[:, None, c]  # with x_i's value in cols
        out = predict_rows(model, task, grid).mean(axis=1)
        return out - out.mean()

    single = {j: pd((j,)) for j in range(4)}
    out = {}
    for j, k in PAIRS:
        joint = pd((j, k))
        denominator = float(np.sum(joint**2))
        key = CONDITIONS[j] + CONDITIONS[k]
        out[key] = (
            float(np.sum((joint - single[j] - single[k]) ** 2) / denominator)
            if denominator > 0.0
            else float("nan")
        )
    return out


def run_job(item: tuple[FitJob, Learner]) -> FitResult:
    """Select, refit on every training state of the domain, predict the test.

    A top-level function so that a process pool can run it.
    """
    job, learner = item
    setting, scores, n_failed = select_setting(job, learner)
    model = _fit(job, setting, learner, np.flatnonzero(job.domain))
    if model is None:
        nan = np.full(job.x_test.shape[:2], np.nan)
        return FitResult(nan, setting.name, scores, n_failed, True)
    pred = predict_rows(model, job.task, job.x_test)
    h2 = (
        friedman_h2(model, job.task, job.h2_sample)
        if job.h2_sample is not None
        else {}
    )
    return FitResult(pred, setting.name, scores, n_failed, False, h2)


def kappa_baseline(kappa: np.ndarray, u: np.ndarray) -> float:
    """The constant rule: ``sum kappa u / sum kappa`` (A2 refit, unclipped).

    Test (a'): this is the initial prediction of the weighted learner.
    """
    return float(np.sum(kappa * u) / np.sum(kappa))


# ------------------------------------------------------------ allocation math
def quad_mse(
    w: np.ndarray, e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
) -> np.ndarray:
    """``V(w) = w^2 E_C + (1 - w)^2 E_P + 2 w (1 - w) C`` (broadcasting)."""
    return w**2 * e_c + (1 - w) ** 2 * e_p + 2 * w * (1 - w) * cross


def excess_kappa(
    w: np.ndarray, kappa: np.ndarray, u: np.ndarray, w_star: np.ndarray
) -> np.ndarray:
    """``V(w) - V(w*) = kappa [(w - u)^2 - (w* - u)^2]`` (test (a))."""
    return kappa * ((w - u) ** 2 - (w_star - u) ** 2)


def realized_score(
    weight: np.ndarray, e_c: np.ndarray, e_p: np.ndarray
) -> np.ndarray:
    """Realized per-state score ``mean_j (w e_C + (1 - w) e_P)^2`` (M-8).

    Inputs ``(n, E)``; the result ``(n,)`` is ``core/state_mse`` for a stored
    rule (test (f1)).
    """
    return np.mean((weight * e_c + (1.0 - weight) * e_p) ** 2, axis=1)


@dataclass
class Allocation:
    """Targets of one horizon on one split (per state).

    ``n_floor`` counts curvatures below ``CURVATURE_FLOOR``.
    """

    kappa: np.ndarray
    u: np.ndarray
    w_star: np.ndarray
    v_star: np.ndarray
    n_floor: int


def allocation_targets(
    e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
) -> Allocation:
    """Curvature, unclipped minimizer, ``w*`` and ``V(w*)`` per state.

    The arithmetic is that of ``oracle.curvature`` and ``oracle_weight``.
    """
    kappa = e_c + e_p - 2.0 * cross
    u = (e_p - cross) / np.maximum(kappa, CURVATURE_FLOOR)
    w_star = np.clip(u, 0.0, 1.0)
    return Allocation(
        kappa,
        u,
        w_star,
        quad_mse(w_star, e_c, e_p, cross),
        int(np.sum(kappa < CURVATURE_FLOOR)),
    )


def kish_size(values: np.ndarray) -> float:
    """Effective size ``(sum x)^2 / sum x^2`` (NaN if ``sum x^2`` is 0)."""
    square = float(np.sum(values**2))
    return float(np.sum(values) ** 2 / square) if square > 0 else float("nan")


@dataclass
class AllocScore:
    """Per-state scores of one allocation rule on the test states.

    ``mse`` is the moment form (oracle) or the realized score (deployable);
    ``excess = mse - V(w*)``; ``excess_w`` the weight-unit excess; ``subst``
    the V-substituted MSE (deployable only, else equal to ``mse``);
    ``weight`` the clipped weights ``(n, r)``.
    """

    mse: np.ndarray
    excess: np.ndarray
    excess_w: np.ndarray
    subst: np.ndarray
    weight: np.ndarray
    n_clipped: int


def score_allocation(
    pred: np.ndarray,
    target: Allocation,
    moments: tuple[np.ndarray, np.ndarray, np.ndarray],
    errors: tuple[np.ndarray, np.ndarray] | None,
) -> AllocScore:
    """Score weights ``(n, r)``: clip to ``[0, 1]`` (counted), then score.

    With ``errors`` (``e_C``, ``e_P`` of shape ``(n, E)``, deployable rows)
    the MSE is the realized score; otherwise the moment form.
    """
    n_clipped = int(np.sum((pred < 0.0) | (pred > 1.0)))
    g = np.clip(pred, 0.0, 1.0)
    u, ws = target.u[:, None], target.w_star[:, None]
    excess_w = np.mean((g - u) ** 2 - (ws - u) ** 2, axis=1)
    e_c, e_p, cross = (m[:, None] for m in moments)
    subst = np.mean(quad_mse(g, e_c, e_p, cross), axis=1)
    if errors is None:
        excess = np.mean(excess_kappa(g, target.kappa[:, None], u, ws), axis=1)
        mse = target.v_star + excess
        subst = mse
    else:
        mse = realized_score(g, *errors)
        excess = mse - target.v_star
    return AllocScore(mse, excess, excess_w, subst, g, n_clipped)


def separation_weight(profile: np.ndarray) -> np.ndarray:
    """The zero-parameter separation formula ``1 / (1 + e^{2(R - O)})``.

    ``profile`` is ``(..., 4)``; the result has its leading shape.
    """
    return expit(2.0 * (profile[..., 1] - profile[..., 0]))


def dependence_bias(
    weight: np.ndarray,
    realized: np.ndarray,
    full: tuple[np.ndarray, np.ndarray, np.ndarray],
    halves: tuple[tuple, tuple],
    half_sizes: tuple[int, int],
    a1_realized: np.ndarray,
) -> dict:
    """Test (f2): the dependence bias of the V substitution (WU-0036 form).

    ``D_i = S_i - Q_i`` with ``Q_i = mean_j V_i(w_ij)``; its standard error
    from the half-draw moments (the oracle Monte Carlo error of ``Q_i``) and
    from the spread of the single-draw squared errors (the realized part).
    Paired: the same with A1 (``w = 0``) subtracted from ``S`` and ``Q``.

    Returns
    -------
    dict
        ``direct`` and ``paired``: ``mean_d``, ``se``, ``z``, ``rel`` (mean
        ``D`` over mean ``Q``) and ``within_margin`` (``|rel| <= 0.05``).
    """
    m_a, m_b = half_sizes
    inv = 1.0 / m_a + 1.0 / m_b
    n_draws = weight.shape[1]
    zero = np.zeros_like(weight)
    out = {}
    for name, paired in (("direct", False), ("paired", True)):

        def q(mom: tuple) -> np.ndarray:
            e_c, e_p, cross = (m[:, None] for m in mom)
            value = quad_mse(weight, e_c, e_p, cross)
            return value - quad_mse(zero, e_c, e_p, cross) if paired else value

        q_a, q_b = q(halves[0]), q(halves[1])
        var = ((q_a - q_b) ** 2 / inv).sum(axis=1) / n_draws**2 + (
            q_a.mean(axis=1) - q_b.mean(axis=1)
        ) ** 2 / inv / (m_a + m_b)
        se = float(np.sqrt(var.sum()) / len(weight))
        q_full = q(full).mean(axis=1)
        s = realized - a1_realized if paired else realized
        d = s - q_full
        scale = float(np.mean(quad_mse(weight, *(m[:, None] for m in full))))
        mean_d = float(d.mean())
        rel = mean_d / scale if scale > 0 else float("nan")
        out[name] = {
            "mean_d": mean_d,
            "se": se,
            "z": mean_d / se if se > 0 else float("nan"),
            "rel": rel,
            "within_margin": bool(abs(rel) <= 0.05),
        }
    return out


# --------------------------------------------------------------- horizon math
@dataclass
class Crossing:
    """The oracle hybrid's horizon per state.

    ``T`` (int, steps, ``H_max`` if censored), ``event``, ``T_c`` (the
    interpolated crossing time; ``inf`` if censored), ``y = ln min(T_c,
    H_max)``, and the counts ``n_first_step`` (``T = 1``: ``T_c = 1``) and
    ``n_exact_theta`` (``e_{T-1} = theta``: ``T_c = T - 1``).
    """

    T: np.ndarray
    event: np.ndarray
    T_c: np.ndarray
    y: np.ndarray
    n_first_step: int
    n_exact_theta: int
    exact: np.ndarray


def crossing_time(
    e_c: np.ndarray,
    e_p: np.ndarray,
    cross: np.ndarray,
    noise: float,
    theta: float,
) -> Crossing:
    """The oracle hybrid's crossing time from full-grid moments ``(n, H_max)``.

    The r.m.s. error ``e_H = sqrt(V_H(w*_H) + rho^2)`` is
    ``oracle.characteristic_horizon``'s; ``T_c = T - 1 + (ln theta - ln
    e_{T-1}) / (ln e_T - ln e_{T-1})`` (math spec M-4).
    """
    target = allocation_targets(e_c, e_p, cross)
    rms = np.sqrt(target.v_star + noise**2)
    exceed = rms > theta
    event = exceed.any(axis=1)
    h_max = rms.shape[1]
    first = np.where(event, exceed.argmax(axis=1) + 1, h_max)
    t_c = np.full(len(first), np.inf)
    first_step = event & (first == 1)
    t_c[first_step] = 1.0
    inner = event & (first > 1)
    rows = np.flatnonzero(inner)
    after = np.log(rms[rows, first[rows] - 1])
    before = np.log(rms[rows, first[rows] - 2])
    t_c[rows] = first[rows] - 1 + (np.log(theta) - before) / (after - before)
    exact = np.zeros(len(first), bool)
    exact[rows] = rms[rows, first[rows] - 2] == theta
    y = np.log(np.minimum(t_c, h_max))
    return Crossing(
        first, event, t_c, y, int(first_step.sum()), int(exact.sum()), exact
    )


def rearrange(q: np.ndarray) -> tuple[np.ndarray, int]:
    """Sort the quantile predictions ``(..., 3)``; count the crossed entries."""
    ordered = np.sort(q, axis=-1)
    crossed = int(np.sum(np.any(ordered != q, axis=-1)))
    return ordered, crossed


def coverage(
    y: np.ndarray, event: np.ndarray, q: np.ndarray, cap: float
) -> dict:
    """Coverage ``P(Y <= q)`` of predictions ``(n, r)`` (M-4).

    Exact for every entry with ``q < cap``; at the cap the indicator is 1 for
    an event and unknown for a censored state, so the all-entry bracket sets
    the unknowns to 0 and to 1.
    """
    yy, ev = y[:, None], np.broadcast_to(event[:, None], q.shape)
    below = q < cap
    hit = yy <= q
    unknown = ~below & ~ev
    return _coverage_record(hit, below, unknown)


def interval_coverage(
    y: np.ndarray,
    event: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    cap: float,
) -> dict:
    """Coverage ``P(q_lo < Y <= q_hi)`` with the same cap rule (upper end)."""
    yy, ev = y[:, None], np.broadcast_to(event[:, None], upper.shape)
    below = upper < cap
    hit = (lower < yy) & (yy <= upper)
    unknown = ~below & ~ev
    return _coverage_record(hit, below, unknown)


def _coverage_record(
    hit: np.ndarray, below: np.ndarray, unknown: np.ndarray
) -> dict:
    n_below = int(below.sum())
    known = hit & ~unknown
    return {
        "coverage_below_cap": (
            float(hit[below].mean()) if n_below else float("nan")
        ),
        "n_below_cap": n_below,
        "n_at_cap": int((~below).sum()),
        "n_unknown": int(unknown.sum()),
        "bracket": [
            float(known.mean()),
            float((known | unknown).mean()),
        ],
    }


def pinball(y: np.ndarray, q: np.ndarray, tau: float) -> np.ndarray:
    """Per-state pinball loss of predictions ``(n, r)``, averaged over rows."""
    return state_loss("pinball", q, {"y": y}, tau)


def comparable_pairs(time: np.ndarray, event: np.ndarray) -> np.ndarray:
    """``P[i, j]``: the pair is comparable under M-4 (i the shorter).

    ``i`` an event with ``t_i < t_j``, or ``t_i = t_j`` with ``i`` an event
    and ``j`` censored. Tied event times and censored pairs are excluded.
    """
    ti, tj = time[:, None], time[None, :]
    ei, ej = event[:, None], event[None, :]
    return ei & ((ti < tj) | ((ti == tj) & ~ej))


def concordance_matrix(score: np.ndarray) -> np.ndarray:
    """``K[i, j] = 1`` if ``s_i < s_j``, ``1/2`` if tied, else 0.

    For scores ``(n, r)`` the mean over the ``r`` columns.
    """
    s = score if score.ndim == 2 else score[:, None]
    out = np.zeros((len(s), len(s)))
    for col in s.T:
        si, sj = col[:, None], col[None, :]
        out += np.where(si < sj, 1.0, np.where(si == sj, 0.5, 0.0))
    return out / s.shape[1]


def harrell_c(
    time: np.ndarray, event: np.ndarray, score: np.ndarray
) -> tuple[float, int, int]:
    """Harrell's C under the M-4 rules; higher score = longer horizon.

    Returns C (NaN with no comparable pair), the comparable pairs, and the
    excluded pairs of tied event times.
    """
    comp = comparable_pairs(time, event)
    n_comp = int(comp.sum())
    tied = np.triu(
        event[:, None] & event[None, :] & (time[:, None] == time[None, :]), 1
    )
    if n_comp == 0:
        return float("nan"), 0, int(tied.sum())
    c = float(np.sum(concordance_matrix(score)[comp]) / n_comp)
    return c, n_comp, int(tied.sum())


def lyapunov_horizon(
    profile: np.ndarray, noise: float, theta: float, steps_per_lt: int
) -> tuple[np.ndarray, np.ndarray]:
    """Zero-parameter Lyapunov form ``T0`` (steps) and its defined mask (M-5).

    ``T0 = (steps_per_lt / I) (ln(theta sqrt(m) / rho) - s)`` with ``s =
    softmin(R, O) = -ln(e^{-2R} + e^{-2O}) / 2``. Undefined (``T0 = inf``)
    where ``I <= 0`` or the log term is ``<= 0``.
    """
    soft = -0.5 * np.logaddexp(-2.0 * profile[..., 0], -2.0 * profile[..., 1])
    head = np.log(theta * np.sqrt(LATENT_DIM) / noise) - soft
    rate = profile[..., 2]
    defined = (rate > 0.0) & (head > 0.0)
    t0 = np.full(rate.shape, np.inf)
    t0[defined] = steps_per_lt * head[defined] / rate[defined]
    return t0, defined


# ---------------------------------------------------------------- bootstrap
def resample_indices(
    n_items: int, n_resamples: int, block: int, rng: np.random.Generator
) -> np.ndarray:
    """The shared moving-block index sets ``(B, n)`` (``statistics``)."""
    return np.stack(
        list(block_resample_indices(n_items, n_resamples, block, rng))
    )


def bootstrap_generator(seed: int, system: str) -> np.random.Generator:
    """The phase J bootstrap stream of one system (a new label)."""
    return make_rng(seed, system, "bootstrap", "phase-J-contrib")


def resampled_mean(
    values: np.ndarray, index: np.ndarray, mask: np.ndarray | None = None
) -> np.ndarray:
    """Mean of ``values`` on every resample (masked: NaN if no state)."""
    if mask is None:
        return values[index].mean(axis=1)
    keep = mask[index]
    count = keep.sum(axis=1)
    total = np.where(keep, values[index], 0.0).sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(count > 0, total / np.maximum(count, 1), np.nan)


def _mean(values: np.ndarray, mask: np.ndarray | None) -> float:
    if mask is None:
        return float(values.mean())
    return float(values[mask].mean()) if mask.any() else float("nan")


def _ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)


def _finite(value: float) -> float | None:
    return float(value) if np.isfinite(value) else None


def _interval(values: np.ndarray, level: float) -> dict:
    lower, upper, n_failed = percentile_interval(values, level)
    return {
        "ci": [_finite(lower), _finite(upper)],
        "ci_raw": (lower, upper),
        "ci_mc_se": list(endpoint_mc_error(values, level)),
        "n_failed_resamples": n_failed,
        "level": level,
    }


def guarded_reading(
    lower: float,
    upper: float,
    n_states: int,
    n_eff: tuple[float, ...] = (),
) -> tuple[str, str | None]:
    """Ratio reading with the 50-state, failure and effective-size guards."""
    reading, reason = ratio_reading_reason(lower, upper, n_states)
    if reason is None and any(
        not np.isfinite(v) or v < MIN_EFFECTIVE for v in n_eff
    ):
        return "undetermined", f"n_eff < {MIN_EFFECTIVE}"
    return reading, reason


def ratio_row(
    num: np.ndarray,
    den: np.ndarray,
    index: np.ndarray,
    level: float,
    *,
    mask: np.ndarray | None = None,
    read: bool = True,
    n_eff: tuple[float, ...] = (),
) -> dict:
    """``mean(num) / mean(den)`` with its paired interval and reading.

    A resample whose denominator mean is ``<= 0`` (or empty) is failed.
    ``read`` False gives an estimate row without a reading.
    """
    point = _ratio(np.array(_mean(num, mask)), np.array(_mean(den, mask)))
    values = _ratio(
        resampled_mean(num, index, mask), resampled_mean(den, index, mask)
    )
    row = {"ratio": _finite(float(point)), **_interval(values, level)}
    lower, upper = row.pop("ci_raw")
    n_states = int(mask.sum()) if mask is not None else len(num)
    row["n_states"] = n_states
    if read:
        row["reading"], row["reason"] = guarded_reading(
            lower, upper, n_states, n_eff
        )
    return row


def difference_row(
    first: np.ndarray,
    second: np.ndarray,
    index: np.ndarray,
    level: float,
    *,
    mask: np.ndarray | None = None,
) -> dict:
    """``mean(first) - mean(second)``, interval, one-sided bootstrap p-value.

    ``p = (1 + #{diff* <= 0 or failed}) / (B + 1)`` (M-3, M-7): small when the
    difference is positive on (almost) every resample.
    """
    diff = first - second
    values = resampled_mean(diff, index, mask)
    row = {"difference": _finite(_mean(diff, mask)), **_interval(values, level)}
    row.pop("ci_raw")
    bad = ~np.isfinite(values) | (values <= 0.0)
    row["p_value"] = float((1 + int(bad.sum())) / (len(values) + 1))
    return row


def add_holm(rows: dict[str, dict], alpha: float = 0.05) -> None:
    """Holm-adjust the ``p_value`` of a family in place (``p_holm``)."""
    names = list(rows)
    adjusted = holm_adjust([rows[k]["p_value"] for k in names])
    for name, p in zip(names, adjusted):
        rows[name]["p_holm"] = p
        rows[name]["detected"] = bool(p <= alpha)


def estimate_row(
    values: np.ndarray, index: np.ndarray, level: float = SHAPLEY_LEVEL
) -> dict:
    """Mean of a per-state array with its interval (no reading)."""
    row = {
        "estimate": float(values.mean()),
        **_interval(resampled_mean(values, index), level),
    }
    row.pop("ci_raw")
    return row


# ------------------------------------------------------------------ Shapley
def shapley_values(loss: dict[tuple[int, ...], np.ndarray]) -> np.ndarray:
    """Shapley shares of the four conditions from the 16 subset losses.

    ``phi_X = sum_{S not containing X} w(|S|) [L(S) - L(S + X)]``, with value
    ``v(S) = -L(S)``, so ``sum_X phi_X = L(empty) - L(F)`` (test (b)). The
    losses may be arrays (one value per resample); the result has a leading
    axis of length 4.
    """
    out = []
    for j in range(len(CONDITIONS)):
        out.append(
            sum(
                shapley_weight(len(s))
                * (loss[s] - loss[tuple(sorted((*s, j)))])
                for s in SUBSETS
                if j not in s
            )
        )
    return np.array(out)


def shapley_rows(
    per_state: dict[tuple[int, ...], np.ndarray], index: np.ndarray
) -> dict:
    """Shapley rows (95% estimates) from per-state losses of the 16 subsets."""
    point = shapley_values({s: float(v.mean()) for s, v in per_state.items()})
    boot = shapley_values(
        {s: resampled_mean(v, index) for s, v in per_state.items()}
    )
    total = float(per_state[()].mean() - per_state[FULL].mean())
    rows = {}
    for j, name in enumerate(CONDITIONS):
        row = {
            "phi": float(point[j]),
            "share": float(point[j] / total) if total != 0 else None,
            **_interval(boot[j], SHAPLEY_LEVEL),
        }
        row.pop("ci_raw")
        rows[name] = row
    return {
        "rows": rows,
        "sum": float(point.sum()),
        "empty_minus_full": total,
    }


# -------------------------------------------------------------- the dataset
SPLIT_NAMES: tuple[str, str, str] = ("construction", "calibration", "test")


@dataclass
class SystemData:
    """The arrays of one system's dump that phase J reads.

    Training is construction followed by calibration (Q-N's order); every
    array of ``train`` and ``test`` is per state. Full-grid moments are
    ``(n, H_max)``.
    """

    system: str
    seed_id: str
    noise: float
    theta: float
    steps_per_lt: int
    horizons: np.ndarray
    ref_index: int
    n_draws: int
    n_oracle: int
    half_sizes: tuple[int, int]
    train: dict[str, np.ndarray]
    test: dict[str, np.ndarray]

    @property
    def h_max(self) -> int:
        return int(self.train["E_C"].shape[1])

    @classmethod
    def from_arrays(cls, arrays: dict[str, np.ndarray]) -> SystemData:
        """Build from a loaded ``states/<system>.npz`` of schema /3.

        Raises
        ------
        ValueError
            If the schema is not /3 or the ``split/`` group is missing.
        """
        schema = str(arrays.get("meta/schema", ""))
        if schema != "lpcstudy.states/3" or "split/test/cp_err" not in arrays:
            raise ValueError(
                f"need a schema /3 dump with split/ (got {schema!r})"
            )
        names = (
            "state_index",
            "delay_clean",
            "delay_eval",
            "E_C",
            "E_P",
            "C",
            "profile_oracle",
            "profile_deployable",
            "T",
            "T_censored",
        )

        def split(s: str, keys: Iterable[str]) -> dict[str, np.ndarray]:
            return {k: arrays[f"split/{s}/{k}"] for k in keys}

        parts = [split(s, names) for s in SPLIT_NAMES[:2]]
        train = {k: np.concatenate([p[k] for p in parts]) for k in names}
        test = split("test", names)
        for key in (
            "cp_err",
            "plp_err",
            "a2_weight",
            "a3_weight",
            "a4_weight",
            "E_C_A",
            "E_P_A",
            "C_A",
            "E_C_B",
            "E_P_B",
            "C_B",
        ):
            test[key] = arrays[f"split/test/{key}"]
        test["a5_weight_href"] = arrays["core/weight_href/A5"]
        for rule in ("A0", "A1", "A2", "A3", "A4", "A5"):
            test[f"state_mse/{rule}"] = arrays[f"core/state_mse/{rule}"]
        halves = arrays["core/half_n_draws"]
        return cls(
            system=str(arrays["meta/system"]),
            seed_id=str(arrays["meta/seed_id"]),
            noise=float(arrays["meta/core_noise"]),
            theta=float(arrays["meta/horizon_threshold"]),
            steps_per_lt=int(arrays["meta/steps_per_lyapunov"]),
            horizons=np.asarray(arrays["core/horizons"]),
            ref_index=int(arrays["core/ref_index"]),
            n_draws=int(arrays["meta/n_eval_draws"]),
            n_oracle=int(arrays["meta/n_oracle_draws"]),
            half_sizes=(int(halves[0]), int(halves[1])),
            train=train,
            test=test,
        )

    def horizon_label(self, h: int) -> str:
        """``"H=8 (0.27 LT)"``: steps and Lyapunov times."""
        return f"H={h} ({h / self.steps_per_lt:.2f} LT)"


def check_stored_scores(data: SystemData) -> dict:
    """Test (f1): ``core/state_mse`` recomputed by :func:`realized_score`.

    A0 (weight 1) and A1 (weight 0), A2, A3, A4 at every evaluation horizon
    and A5 at ``H_ref``; the largest relative difference of each, and whether
    every one is within 1e-12.
    """
    t = data.test
    e_c, e_p = t["cp_err"], t["plp_err"]
    weights = {
        "A0": np.ones_like(e_c),
        "A1": np.zeros_like(e_c),
        "A2": t["a2_weight"],
        "A3": t["a3_weight"],
        "A4": t["a4_weight"],
    }
    out = {}
    for rule, w in weights.items():
        stored = t[f"state_mse/{rule}"]
        mine = np.stack(
            [
                realized_score(w[:, :, h], e_c[:, :, h], e_p[:, :, h])
                for h in range(e_c.shape[2])
            ],
            axis=1,
        )
        out[rule] = float(np.max(np.abs(mine - stored) / np.abs(stored)))
    ref = data.ref_index
    a5 = realized_score(t["a5_weight_href"], e_c[:, :, ref], e_p[:, :, ref])
    stored = t["state_mse/A5"][:, ref]
    out["A5"] = float(np.max(np.abs(a5 - stored) / np.abs(stored)))
    return {
        "max_rel_diff": out,
        "within_1e-12": bool(all(v <= 1e-12 for v in out.values())),
    }


def qn_cross_check(
    data: SystemData, seed: int, n_resamples: int, block: int
) -> dict:
    """Test (g): WU-0039b rows (b1), (b2) recomputed from the dump.

    ``ablation.profile_ablation_block`` on the oracle profile with Q-N's
    targets (``w*(H_ref)`` from the dumped split moments by the arithmetic of
    ``oracle_weight``, ``ln T`` from ``split/T``), Q-N's regressor and Q-N's
    resamples (a fresh ``make_rng(seed, system, "bootstrap", "Q-N")``, shared
    on purpose so that the rows can be compared with the run's leaves).
    """
    from .ablation import PROFILE_LEVEL, profile_ablation_block

    col = int(data.horizons[data.ref_index]) - 1

    def targets(part: dict) -> tuple[np.ndarray, np.ndarray]:
        curv = (
            part["E_C"][:, col] + part["E_P"][:, col] - 2.0 * part["C"][:, col]
        )
        raw = (part["E_P"][:, col] - part["C"][:, col]) / np.maximum(
            curv, CURVATURE_FLOOR
        )
        return np.clip(raw, 0.0, 1.0), np.log(part["T"])

    w_train, t_train = targets(data.train)
    w_test, t_test = targets(data.test)
    return profile_ablation_block(
        data.train["profile_oracle"],
        data.test["profile_oracle"],
        w_train,
        w_test,
        t_train,
        t_test,
        seed=seed,
        n_resamples=n_resamples,
        block=block,
        boot_seed=make_rng(seed, data.system, "bootstrap", "Q-N"),
        level=PROFILE_LEVEL,
        horizon_cap=float(np.log(data.h_max)),
    )


# ------------------------------------------------------------- the inputs
PROFILES: tuple[str, str] = ("oracle", "deployable")
"""The two profiles: oracle (moment scoring) and deployable (realized)."""


def profile_inputs(data: SystemData, kind: str, split: str) -> np.ndarray:
    """The profile ``(n, r, 4)`` of a split (``r = 1`` for the oracle)."""
    part = data.train if split == "train" else data.test
    if kind == "oracle":
        return part["profile_oracle"][:, None, :]
    return part["profile_deployable"]


def delay_inputs(data: SystemData, kind: str, split: str) -> np.ndarray:
    """The delay vector ``X_t`` ``(n, r, D)``: clean (oracle) or noisy."""
    part = data.train if split == "train" else data.test
    if kind == "oracle":
        return part["delay_clean"][:, None, :]
    return part["delay_eval"]


def swap_inputs(data: SystemData, column: int, split: str) -> np.ndarray:
    """The oracle profile with one coordinate replaced by its estimate."""
    oracle = profile_inputs(data, "oracle", split)
    deployable = profile_inputs(data, "deployable", split)
    out = np.repeat(oracle, deployable.shape[1], axis=1)
    out[..., column] = deployable[..., column]
    return out


def input_sets(
    data: SystemData, kind: str, split: str
) -> dict[str, np.ndarray]:
    """Every learned input set of a profile, keyed by name.

    The 15 non-empty subsets (letters), ``X`` (the delay vector) and ``X+F``.
    """
    profile = profile_inputs(data, kind, split)
    delay = delay_inputs(data, kind, split)
    sets = {subset_key(s): profile[..., list(s)] for s in SUBSETS[1:]}
    sets["X"] = delay
    sets["X+F"] = np.concatenate(
        [delay, np.broadcast_to(profile, (*delay.shape[:2], 4))], axis=-1
    )
    return sets


def _alloc_aux(target: Allocation) -> dict[str, np.ndarray]:
    return {"kappa": target.kappa, "u": target.u, "w_star": target.w_star}


def allocation_jobs(
    data: SystemData, column: int, kind: str, train: Allocation
) -> dict[str, FitJob]:
    """The allocation fits of one horizon and profile (A, D).

    For every input set: ``A/<set>`` (u, weight ``kappa / mean kappa``, loss
    ``kappa_excess``) and ``W/<set>`` (u, unit weight, ``unit_excess``). The
    deployable profile adds the four swap hybrids ``A/swap-<X>`` (D).
    """
    order = data.train["state_index"]
    weight = train.kappa / train.kappa.mean()
    everywhere = np.ones(len(train.u), bool)
    jobs = {}
    sets = input_sets(data, kind, "train")
    tests = input_sets(data, kind, "test")
    if kind == "deployable":
        for j, name in enumerate(CONDITIONS):
            sets[f"swap-{name}"] = swap_inputs(data, j, "train")
            tests[f"swap-{name}"] = swap_inputs(data, j, "test")
    for name, x in sets.items():
        jobs[f"A/{name}"] = FitJob(
            "regression",
            x,
            train.u,
            weight,
            everywhere,
            order,
            tests[name],
            "kappa_excess",
            _alloc_aux(train),
        )
        if not name.startswith("swap"):
            jobs[f"W/{name}"] = FitJob(
                "regression",
                x,
                train.u,
                None,
                everywhere,
                order,
                tests[name],
                "unit_excess",
                _alloc_aux(train),
            )
    return jobs


def _logit(u: np.ndarray, rows: np.ndarray) -> np.ndarray:
    inner = np.where(rows, u, 0.5)
    return np.log(inner / (1.0 - inner))


def pair_constraints() -> dict[str, list[list[int]] | None]:
    """``interaction_cst`` of B: additive, each pair, and none (full)."""
    out: dict[str, list[list[int]] | None] = {
        "add": [[0], [1], [2], [3]],
    }
    for j, k in PAIRS:
        rest = [[c] for c in range(4) if c not in (j, k)]
        out[CONDITIONS[j] + CONDITIONS[k]] = [[j, k], *rest]
    out["full"] = None
    return out


def pair_jobs(base: FitJob, full: bool = True) -> dict[str, FitJob]:
    """The B variants of a base job (additive, six pairs, optionally full)."""
    out = {}
    for name, cst in pair_constraints().items():
        if name == "full" and not full:
            continue
        job = FitJob(**{**base.__dict__, "cst": cst})
        if name != "full":
            job.h2_sample = None
        out[name] = job
    return out


def interaction_parts(
    data: SystemData,
    column: int,
    kind: str,
    train: Allocation,
    test: Allocation,
) -> dict[str, tuple[FitJob, np.ndarray, str]]:
    """The base jobs of B for allocation: part -> (job, test mask, loss).

    ``logit`` (logit u on interior states, squared loss), ``zero`` (1{w* =
    0}, log loss), ``one`` (1{w* = 1}, only where its test share exceeds 5%)
    and ``decision`` (kappa-weighted u, the u scale, labeled as the link's).
    """
    order = data.train["state_index"]
    x = profile_inputs(data, kind, "train")
    x_test = profile_inputs(data, kind, "test")
    interior = (train.u > 0.0) & (train.u < INTERIOR_LIMIT)
    interior_test = (test.u > 0.0) & (test.u < INTERIOR_LIMIT)
    everywhere = np.ones(len(train.u), bool)
    sample = x_test[
        np.linspace(
            0, len(x_test) - 1, min(INTERACTION_SAMPLE, len(x_test))
        ).astype(int),
        0,
        :,
    ]
    y_logit = _logit(train.u, interior)
    parts = {
        "logit": (
            FitJob(
                "regression",
                x,
                y_logit,
                None,
                interior,
                order,
                x_test,
                "squared",
                {"y": y_logit},
                h2_sample=sample,
            ),
            interior_test,
            "squared",
        ),
    }
    for name, flag, flag_test in (
        ("zero", train.u <= 0.0, test.u <= 0.0),
        ("one", train.u >= INTERIOR_LIMIT, test.u >= INTERIOR_LIMIT),
    ):
        if name == "one" and flag_test.mean() <= INDICATOR_SHARE:
            continue
        y = flag.astype(float)
        parts[name] = (
            FitJob(
                "classifier",
                x,
                y,
                None,
                everywhere,
                order,
                x_test,
                "log_loss",
                {"y": y},
            ),
            np.ones(len(test.u), bool),
            "log_loss",
        )
    weight = train.kappa / train.kappa.mean()
    parts["decision"] = (
        FitJob(
            "regression",
            x,
            train.u,
            weight,
            everywhere,
            order,
            x_test,
            "kappa_excess",
            _alloc_aux(train),
        ),
        np.ones(len(test.u), bool),
        "kappa_excess",
    )
    return parts


def horizon_jobs(
    data: SystemData, kind: str, crossing: Crossing
) -> dict[str, FitJob]:
    """Quantile fits ``Q<tau>/<set>`` of the horizon on every input set."""
    order = data.train["state_index"]
    cap = float(np.log(data.h_max))
    everywhere = np.ones(len(crossing.y), bool)
    sets = input_sets(data, kind, "train")
    tests = input_sets(data, kind, "test")
    if kind == "deployable":
        for j, name in enumerate(CONDITIONS):
            sets[f"swap-{name}"] = swap_inputs(data, j, "train")
            tests[f"swap-{name}"] = swap_inputs(data, j, "test")
    jobs = {}
    for name, x in sets.items():
        for tau in TAUS:
            jobs[f"Q{tau:g}/{name}"] = FitJob(
                "quantile",
                x,
                crossing.y,
                None,
                everywhere,
                order,
                tests[name],
                "pinball",
                {"y": crossing.y},
                tau=tau,
                cap=cap,
            )
    return jobs


def horizon_pair_base(
    data: SystemData, kind: str, crossing: Crossing
) -> FitJob:
    """The base median model of B for the horizon (log scale)."""
    x_test = profile_inputs(data, kind, "test")
    sample = x_test[
        np.linspace(
            0, len(x_test) - 1, min(INTERACTION_SAMPLE, len(x_test))
        ).astype(int),
        0,
        :,
    ]
    return FitJob(
        "quantile",
        profile_inputs(data, kind, "train"),
        crossing.y,
        None,
        np.ones(len(crossing.y), bool),
        data.train["state_index"],
        x_test,
        "pinball",
        {"y": crossing.y},
        tau=0.5,
        cap=float(np.log(data.h_max)),
        h2_sample=sample,
    )


# ----------------------------------------------------------- assembling rows
def _setting_record(result: FitResult) -> dict:
    return {
        "setting": result.setting,
        "cv_loss": result.cv_loss,
        "n_cv_fold_failed": result.n_fold_failed,
        "fit_failed": result.failed,
    }


def pair_rows(
    losses: dict[str, np.ndarray],
    index: np.ndarray,
    mask: np.ndarray | None = None,
) -> dict:
    """B's statistics from per-state test losses of ``add``, the pairs, ``full``.

    Per pair ``Delta = L(add) - L(pair)`` with its interval at ``1 - 0.05/6``,
    its bootstrap p-value, Holm over the six pairs, and the loss ratio
    ``L(add) / L(pair)`` read by the 1.05 table at the same level (math spec
    M-3). ``ceiling`` is ``L(add) - L(full)`` (if ``full`` is given).
    """
    level = 1.0 - 0.05 / len(PAIRS)
    rows = {}
    for j, k in PAIRS:
        name = CONDITIONS[j] + CONDITIONS[k]
        row = difference_row(
            losses["add"], losses[name], index, level, mask=mask
        )
        row["loss_ratio"] = ratio_row(
            losses["add"], losses[name], index, level, mask=mask
        )
        row["primary"] = name in PRIMARY_PAIRS
        rows[name] = row
    add_holm(rows)
    out = {"pairs": rows, "level": level}
    if "full" in losses:
        out["ceiling"] = difference_row(
            losses["add"], losses["full"], index, SHAPLEY_LEVEL, mask=mask
        )
    out["loss_add"] = _mean(losses["add"], mask)
    return out


@dataclass
class Context:
    """Shared per-system state of the assembly (index sets, scales)."""

    data: SystemData
    index: np.ndarray


def allocation_block(
    ctx: Context,
    column: int,
    kind: str,
    results: dict[str, FitResult],
    train: Allocation,
    test: Allocation,
) -> dict:
    """A and D for allocation at one horizon and profile."""
    data, index = ctx.data, ctx.index
    t = data.test
    moments = tuple(
        t[k][:, data.horizons[column] - 1] for k in ("E_C", "E_P", "C")
    )
    errors = None
    if kind == "deployable":
        errors = (t["cp_err"][:, :, column], t["plp_err"][:, :, column])
    r = 1 if kind == "oracle" else data.n_draws
    n = len(test.u)

    def score(pred: np.ndarray) -> AllocScore:
        return score_allocation(pred, test, moments, errors)

    constant = kappa_baseline(train.kappa, train.u)
    unit_constant = float(train.u.mean())
    scores: dict[str, AllocScore] = {}
    unit_scores: dict[str, AllocScore] = {}
    records: dict[str, dict] = {}
    scores["none"] = score(np.full((n, r), constant))
    unit_scores["none"] = score(np.full((n, r), unit_constant))
    for key, result in results.items():
        family, name = key.split("/", 1)
        target = scores if family == "A" else unit_scores
        target[name] = score(result.pred)
        records.setdefault(name, {})[family] = _setting_record(result)
    profile = profile_inputs(data, kind, "test")
    scores["separation"] = score(separation_weight(profile))
    if kind == "deployable":
        for rule in ("A2", "A3", "A4"):
            scores[f"{rule} (stored)"] = score(
                t[f"{rule.lower()}_weight"][:, :, column]
            )
        if column == data.ref_index:
            scores["A5 (stored)"] = score(t["a5_weight_href"])

    n_eff_kappa = kish_size(test.kappa)
    full_key = subset_key(FULL)

    def n_eff_of(reference: str) -> tuple[float, float]:
        return (n_eff_kappa, kish_size(scores[reference].excess))

    subset_rows = {}
    for s in SUBSETS:
        key = subset_key(s)
        sc, usc = scores[key], unit_scores[key]
        subset_rows[key] = {
            "mse": float(sc.mse.mean()),
            "L_A": float(sc.excess.mean()),
            "L_w": float(usc.excess_w.mean()),
            "n_pred_clipped": sc.n_clipped,
            "n_pred_clipped_w": usc.n_clipped,
            "fit": records.get(key, {"A": "closed form", "W": "closed form"}),
            "G": ratio_row(
                scores["none"].excess - sc.excess,
                scores["none"].excess,
                index,
                SHAPLEY_LEVEL,
                read=False,
            ),
            "mse_vs_separation": ratio_row(
                sc.mse,
                scores["separation"].mse,
                index,
                SHAPLEY_LEVEL,
                n_eff=n_eff_of("separation"),
            ),
        }

    level_a = 1.0 - 0.05 / len(CONDITIONS)
    drop = {}
    for j, name in enumerate(CONDITIONS):
        without = subset_key(tuple(c for c in FULL if c != j))
        row = difference_row(
            scores[without].mse, scores[full_key].mse, index, level_a
        )
        row["mse_ratio"] = ratio_row(
            scores[without].mse,
            scores[full_key].mse,
            index,
            level_a,
            n_eff=n_eff_of(full_key),
        )
        row["excess_ratio"] = ratio_row(
            scores[without].excess,
            scores[full_key].excess,
            index,
            level_a,
            read=False,
        )
        row["L_w_ratio"] = ratio_row(
            unit_scores[without].excess_w,
            unit_scores[full_key].excess_w,
            index,
            level_a,
            read=False,
        )
        drop[name] = row
    add_holm(drop)

    ladder = _allocation_ladder(ctx, kind, scores, n_eff_of, column)
    dependence = {}
    if kind == "deployable":
        a1 = realized_score(np.zeros_like(errors[0]), *errors)
        halves = tuple(
            tuple(
                t[f"{m}_{tag}"][:, data.horizons[column] - 1]
                for m in ("E_C", "E_P", "C")
            )
            for tag in ("A", "B")
        )
        for name, sc in scores.items():
            dependence[name] = dependence_bias(
                sc.weight, sc.mse, moments, halves, data.half_sizes, a1
            )
    oracle_mc = (
        test.kappa
        * (
            np.clip(_u_half(t, data, column, "A"), 0, 1)
            - np.clip(_u_half(t, data, column, "B"), 0, 1)
        )
        ** 2
        / 4.0
    )
    return {
        "horizon": data.horizon_label(int(data.horizons[column])),
        "profile": kind,
        "scoring": "moment form" if kind == "oracle" else "realized per draw",
        "n_states": n,
        "n_eff_kappa": n_eff_kappa,
        "n_eff_constant_excess": kish_size(scores["none"].excess),
        "constant_weight": {"kappa": constant, "unit": unit_constant},
        "share_u_below_0": float(np.mean(test.u <= 0.0)),
        "share_u_above_1": float(np.mean(test.u >= 1.0)),
        "n_curvature_floor": test.n_floor + train.n_floor,
        "oracle_mc_bias_over_constant_excess": float(
            oracle_mc.mean() / scores["none"].excess.mean()
        ),
        "subsets": subset_rows,
        "drop_one": drop,
        "shapley_L_A": shapley_rows(
            {s: scores[subset_key(s)].mse for s in SUBSETS}, index
        ),
        "shapley_L_w": shapley_rows(
            {s: unit_scores[subset_key(s)].excess_w for s in SUBSETS}, index
        ),
        "ladder": ladder,
        "dependence_bias": dependence,
        "_scores": scores,
    }


def _u_half(t: dict, data: SystemData, column: int, tag: str) -> np.ndarray:
    h = data.horizons[column] - 1
    return allocation_targets(
        t[f"E_C_{tag}"][:, h], t[f"E_P_{tag}"][:, h], t[f"C_{tag}"][:, h]
    ).u


ALLOCATION_RUNGS: dict[str, tuple[str, ...]] = {
    "oracle": (
        "none",
        "separation",
        "RO",
        "R",
        "O",
        "I",
        "N",
        "ROIN",
        "X",
        "X+F",
    ),
    "deployable": (
        "none",
        "A2 (stored)",
        "separation",
        "A4 (stored)",
        "RO",
        "R",
        "O",
        "I",
        "N",
        "ROIN",
        "X",
        "A3 (stored)",
        "X+F",
    ),
}
"""The D ladder of allocation, simplest first (plan section 4.D)."""


def _allocation_ladder(
    ctx: Context, kind: str, scores: dict, n_eff_of, column: int
) -> dict:
    index = ctx.index
    rungs = [k for k in ALLOCATION_RUNGS[kind] if k in scores]
    if kind == "deployable" and "A5 (stored)" in scores:
        rungs.insert(rungs.index("ROIN"), "A5 (stored)")
    full = "ROIN"
    family = [k for k in rungs if k != full]
    level = 1.0 - 0.05 / len(family)
    vs_full = {}
    for name in family:
        row = difference_row(scores[name].mse, scores[full].mse, index, level)
        row["mse_ratio"] = ratio_row(
            scores[name].mse,
            scores[full].mse,
            index,
            level,
            n_eff=n_eff_of(full),
        )
        row["excess_ratio"] = ratio_row(
            scores[name].excess, scores[full].excess, index, level, read=False
        )
        vs_full[name] = row
    add_holm(vs_full)
    vs_below = {}
    for below, name in zip(rungs[:-1], rungs[1:]):
        vs_below[f"{below} -> {name}"] = ratio_row(
            scores[below].mse,
            scores[name].mse,
            index,
            SHAPLEY_LEVEL,
            n_eff=n_eff_of(name),
        )
    return {
        "rungs": rungs,
        "level": level,
        "vs_full": vs_full,
        "vs_below": vs_below,
        "mse": {k: float(scores[k].mse.mean()) for k in rungs},
        "L_A": {k: float(scores[k].excess.mean()) for k in rungs},
    }


def gap_block(ctx: Context, oracle: dict, deployable: dict) -> dict:
    """Theory and estimation gaps of allocation at one horizon (D).

    Theory gap ``L_A(oracle F)``: an upper bound on what exact conditions
    leave (the P3 floor plus the learner's error, M-2 rule 3). Estimation gap
    ``L_A(deployable F) - L_A(oracle F)``, and per condition the hybrid with
    that one coordinate estimated.
    """
    index = ctx.index
    o, d = oracle["_scores"], deployable["_scores"]
    full = "ROIN"
    out = {
        "theory_gap_upper_bound": estimate_row(o[full].excess, index),
        "estimation_gap": estimate_row(d[full].excess - o[full].excess, index),
        "by_condition": {},
    }
    for name in CONDITIONS:
        key = f"swap-{name}"
        if key in d:
            out["by_condition"][name] = estimate_row(
                d[key].excess - o[full].excess, index
            )
    return out


def horizon_block(
    ctx: Context,
    kind: str,
    results: dict[str, FitResult],
    train: Crossing,
    test: Crossing,
) -> dict:
    """A and D for the horizon decision on one profile."""
    data, index = ctx.data, ctx.index
    cap = float(np.log(data.h_max))
    n = len(test.y)
    r = 1 if kind == "oracle" else data.n_draws
    preds: dict[str, np.ndarray] = {}
    counts: dict[str, dict] = {}
    names = sorted({k.split("/", 1)[1] for k in results})
    for name in names:
        raw = np.stack(
            [results[f"Q{tau:g}/{name}"].pred for tau in TAUS], axis=-1
        )
        ordered, crossed = rearrange(raw)
        capped = np.minimum(ordered, cap)
        preds[name] = capped
        counts[name] = {
            "n_crossed": crossed,
            "n_capped": int(np.sum(ordered > cap)),
            "fit": {
                f"{tau:g}": _setting_record(results[f"Q{tau:g}/{name}"])
                for tau in TAUS
            },
        }
    const = np.quantile(train.y, TAUS)
    preds["none"] = np.broadcast_to(const, (n, r, 3)).copy()
    counts["none"] = {"n_crossed": 0, "n_capped": 0, "fit": "closed form"}
    # Lyapunov quantile (M-5): 6 constants, no fitted function of F.
    train_prof = profile_inputs(data, kind, "train")
    test_prof = profile_inputs(data, kind, "test")
    t0_train, ok_train = lyapunov_horizon(
        train_prof, data.noise, data.theta, data.steps_per_lt
    )
    t0_test, ok_test = lyapunov_horizon(
        test_prof, data.noise, data.theta, data.steps_per_lt
    )
    y_rows = np.broadcast_to(train.y[:, None], ok_train.shape)
    resid = np.quantile(y_rows[ok_train] - np.log(t0_train[ok_train]), TAUS)
    other = (
        np.quantile(y_rows[~ok_train], TAUS)
        if (~ok_train).any()
        else np.quantile(train.y, TAUS)
    )
    lyap = np.where(
        ok_test[..., None],
        np.log(np.where(ok_test, t0_test, 1.0))[..., None] + resid,
        other,
    )
    ordered, crossed = rearrange(lyap)
    preds["lyapunov"] = np.minimum(ordered, cap)
    counts["lyapunov"] = {
        "n_crossed": crossed,
        "n_capped": int(np.sum(ordered > cap)),
        "n_undefined_train": int((~ok_train).sum()),
        "n_undefined_test": int((~ok_test).sum()),
        "fit": "6 constants",
    }

    time = np.minimum(test.T_c, data.h_max)
    comp = comparable_pairs(time, test.event)
    count_matrix = _count_matrix(index, n)
    comp_total = np.einsum(
        "bi,ij,bj->b",
        count_matrix,
        comp.astype(float),
        count_matrix,
        optimize=True,
    )

    def c_row(score: np.ndarray) -> dict:
        k = concordance_matrix(score) * comp
        point = float(k.sum() / comp.sum()) if comp.any() else float("nan")
        num = np.einsum(
            "bi,ij,bj->b", count_matrix, k, count_matrix, optimize=True
        )
        values = _ratio(num, comp_total)
        row = {"c_index": _finite(point), **_interval(values, SHAPLEY_LEVEL)}
        row.pop("ci_raw")
        return row

    pin = {k: pinball(test.y, v[..., 1], 0.5) for k, v in preds.items()}
    rows = {}
    for name, q in preds.items():
        rows[name] = {
            "pinball_0.5": float(pin[name].mean()),
            "c_index": c_row(q[..., 1]),
            "coverage": {
                f"{tau:g}": coverage(test.y, test.event, q[..., i], cap)
                for i, tau in enumerate(TAUS)
            },
            "coverage_80": interval_coverage(
                test.y, test.event, q[..., 0], q[..., 2], cap
            ),
            **counts[name],
        }
    lyapunov_rank = c_row(t0_test)  # undefined form: T0 = inf, ties 1/2

    full_key = "ROIN"
    level_a = 1.0 - 0.05 / len(CONDITIONS)
    drop = {}
    for j, name in enumerate(CONDITIONS):
        without = subset_key(tuple(c for c in FULL if c != j))
        row = difference_row(pin[without], pin[full_key], index, level_a)
        row["pinball_ratio"] = ratio_row(
            pin[without], pin[full_key], index, level_a
        )
        drop[name] = row
    add_holm(drop)

    rungs = [
        k
        for k in (
            "none",
            "lyapunov",
            "RO",
            "R",
            "O",
            "I",
            "N",
            full_key,
            "X",
            "X+F",
        )
        if k in pin
    ]
    family = [k for k in rungs if k != full_key]
    level_d = 1.0 - 0.05 / len(family)
    vs_full = {}
    for name in family:
        row = difference_row(pin[name], pin[full_key], index, level_d)
        row["pinball_ratio"] = ratio_row(
            pin[name], pin[full_key], index, level_d
        )
        vs_full[name] = row
    add_holm(vs_full)
    vs_below = {
        f"{a} -> {b}": ratio_row(pin[a], pin[b], index, SHAPLEY_LEVEL)
        for a, b in zip(rungs[:-1], rungs[1:])
    }
    return {
        "profile": kind,
        "target": "Y = ln min(T_c, H_max), oracle hybrid at theta",
        "n_states": n,
        "n_censored": int((~test.event).sum()),
        "share_censored": float(np.mean(~test.event)),
        "rows": rows,
        "lyapunov_rank": lyapunov_rank,
        "drop_one": drop,
        "shapley_pinball": shapley_rows(
            {s: pin[subset_key(s)] for s in SUBSETS}, index
        ),
        "ladder": {
            "rungs": rungs,
            "level": level_d,
            "vs_full": vs_full,
            "vs_below": vs_below,
        },
        "_pinball": pin,
    }


def _count_matrix(index: np.ndarray, n: int) -> np.ndarray:
    """How often each state occurs in each resample, ``(B, n)``."""
    out = np.zeros((len(index), n))
    rows = np.repeat(np.arange(len(index)), index.shape[1])
    np.add.at(out, (rows, index.ravel()), 1.0)
    return out


def horizon_gap_block(ctx: Context, oracle: dict, deployable: dict) -> dict:
    """Theory and estimation gaps of the horizon on the pinball loss (D)."""
    index = ctx.index
    o, d = oracle["_pinball"], deployable["_pinball"]
    out = {
        "theory_pinball_upper_bound": estimate_row(o["ROIN"], index),
        "estimation_gap": estimate_row(d["ROIN"] - o["ROIN"], index),
        "by_condition": {},
    }
    for name in CONDITIONS:
        key = f"swap-{name}"
        if key in d:
            out["by_condition"][name] = estimate_row(d[key] - o["ROIN"], index)
    return out


# --------------------------------------------------------------- the system
Mapper = Callable[[Callable, Iterable], Iterable]


def analyze_system(
    data: SystemData,
    seed: int,
    *,
    n_resamples: int,
    block: int,
    mapper: Mapper = map,
    grid: tuple[Setting, ...] = GRID,
    profiles: tuple[str, ...] = PROFILES,
) -> dict:
    """Experiments A, B and D for one system of one run.

    Parameters
    ----------
    data : SystemData
        The system's dump.
    seed : int
        The run's master seed (``config.seed``): the bootstrap stream
        (:func:`bootstrap_generator`) and the learner's scikit-learn seed.
    n_resamples, block : int
        Bootstrap resamples and block length (the run's configuration).
    mapper : callable, optional
        ``map``-like executor of :func:`run_job` (a process pool's ``map``).
    grid : tuple[Setting, ...], optional
        The learner's grid (``GRID``).
    profiles : tuple[str, ...], optional
        Profiles to analyze.

    Returns
    -------
    dict
        ``label``, ``checks`` (f1, the ``T_c`` counts), ``allocation``,
        ``interactions``, ``gaps``, ``horizon``.
    """
    learner = Learner(seed=seed, grid=grid)
    index = resample_indices(
        len(data.test["T"]),
        n_resamples,
        block,
        bootstrap_generator(seed, data.system),
    )
    ctx = Context(data, index)
    train_cross = crossing_time(
        data.train["E_C"],
        data.train["E_P"],
        data.train["C"],
        data.noise,
        data.theta,
    )
    test_cross = crossing_time(
        data.test["E_C"],
        data.test["E_P"],
        data.test["C"],
        data.noise,
        data.theta,
    )
    for part, cross in (("train", train_cross), ("test", test_cross)):
        if not np.array_equal(cross.T, getattr(data, part)["T"]) or not (
            np.array_equal(~cross.event, getattr(data, part)["T_censored"])
        ):
            raise ValueError(
                f"{part}: the recomputed horizon differs from split/T"
            )
    for cross in (train_cross, test_cross):
        check = np.isfinite(cross.T_c) & ~cross.exact
        if np.any(np.ceil(cross.T_c[check]) != cross.T[check]):
            raise ValueError("ceil(T_c) differs from T")

    jobs: dict[tuple, FitJob] = {}
    targets: dict[int, tuple[Allocation, Allocation]] = {}
    parts_meta: dict[tuple, tuple[np.ndarray, str]] = {}
    for column, h in enumerate(data.horizons):
        tr = allocation_targets(
            *(data.train[k][:, h - 1] for k in ("E_C", "E_P", "C"))
        )
        te = allocation_targets(
            *(data.test[k][:, h - 1] for k in ("E_C", "E_P", "C"))
        )
        targets[column] = (tr, te)
        for kind in profiles:
            for key, job in allocation_jobs(data, column, kind, tr).items():
                jobs[("alloc", column, kind, key)] = job
            for part, (base, mask, loss) in interaction_parts(
                data, column, kind, tr, te
            ).items():
                parts_meta[(column, kind, part)] = (mask, loss)
                variants = pair_jobs(base, full=part != "decision")
                for name, job in variants.items():
                    jobs[("pair", column, kind, part, name)] = job
    for kind in profiles:
        for key, job in horizon_jobs(data, kind, train_cross).items():
            jobs[("horizon", kind, key)] = job
        for name, job in pair_jobs(
            horizon_pair_base(data, kind, train_cross)
        ).items():
            jobs[("pair", "horizon", kind, "median", name)] = job

    keys = list(jobs)
    results = dict(
        zip(keys, mapper(run_job, [(jobs[k], learner) for k in keys]))
    )

    out: dict = {
        "label": LABEL.format(seed_id=data.seed_id),
        "system": data.system,
        "seed_id": data.seed_id,
        "n_resamples": n_resamples,
        "block": block,
        "grid": [s.__dict__ for s in grid],
        "checks": {
            "f1_state_mse": check_stored_scores(data),
            "crossing_time": {
                "train": {
                    "n_first_step": train_cross.n_first_step,
                    "n_exact_theta": train_cross.n_exact_theta,
                },
                "test": {
                    "n_first_step": test_cross.n_first_step,
                    "n_exact_theta": test_cross.n_exact_theta,
                },
                "ceil_T_c_equals_T": True,
            },
        },
        "allocation": {},
        "interactions": {},
        "gaps": {},
        "horizon": {},
    }
    for column, h in enumerate(data.horizons):
        label = str(int(h))
        tr, te = targets[column]
        blocks = {}
        for kind in profiles:
            mine = {
                key[3]: res
                for key, res in results.items()
                if key[0] == "alloc" and key[1] == column and key[2] == kind
            }
            blocks[kind] = allocation_block(ctx, column, kind, mine, tr, te)
            out["interactions"].setdefault(label, {})[kind] = (
                _interaction_record(ctx, results, column, kind, parts_meta, te)
            )
        if set(profiles) == set(PROFILES):
            out["gaps"][label] = gap_block(
                ctx, blocks["oracle"], blocks["deployable"]
            )
        if column == data.ref_index and "deployable" in blocks:
            sep = blocks["deployable"]["_scores"]["separation"].weight
            stored = data.test["a4_weight"][:, :, column]
            out["checks"]["separation_vs_stored_A4_max_abs"] = float(
                np.max(np.abs(sep - stored))
            )
        for kind in profiles:
            blocks[kind].pop("_scores")
        out["allocation"][label] = blocks
    hblocks = {}
    for kind in profiles:
        mine = {
            key[2]: res
            for key, res in results.items()
            if key[0] == "horizon" and key[1] == kind
        }
        hblocks[kind] = horizon_block(ctx, kind, mine, train_cross, test_cross)
        cap = float(np.log(data.h_max))
        losses = {
            name: pinball(test_cross.y, np.minimum(results[key].pred, cap), 0.5)
            for key in results
            if key[:4] == ("pair", "horizon", kind, "median")
            for name in (key[4],)
        }
        hblocks[kind]["interactions"] = pair_rows(losses, index)
        hblocks[kind]["interactions"]["friedman_h2_full"] = results[
            ("pair", "horizon", kind, "median", "full")
        ].h2
    if set(profiles) == set(PROFILES):
        out["horizon_gaps"] = horizon_gap_block(
            ctx, hblocks["oracle"], hblocks["deployable"]
        )
    for kind in profiles:
        hblocks[kind].pop("_pinball")
    out["horizon"] = hblocks
    return out


def _interaction_record(
    ctx: Context,
    results: dict,
    column: int,
    kind: str,
    parts_meta: dict,
    test: Allocation,
) -> dict:
    """B for allocation at one horizon and profile, part by part."""
    out = {}
    for (col, k, part), (mask, loss) in parts_meta.items():
        if col != column or k != kind:
            continue
        found = {
            key[4]: res
            for key, res in results.items()
            if key[:4] == ("pair", column, kind, part)
        }
        if any(res.failed for res in found.values()):
            out[part] = {
                "reading": "undetermined",
                "reason": "single-class training set",
            }
            continue
        aux = (
            {"y": _logit(test.u, mask)}
            if part == "logit"
            else {"y": (test.u <= 0.0).astype(float)}
            if part == "zero"
            else {"y": (test.u >= INTERIOR_LIMIT).astype(float)}
            if part == "one"
            else _alloc_aux(test)
        )
        losses = {
            name: state_loss(loss, res.pred, aux) for name, res in found.items()
        }
        record = pair_rows(
            losses, ctx.index, mask=mask if part == "logit" else None
        )
        record["scale"] = {
            "logit": "logit u, interior states (primary)",
            "zero": "log-odds of 1{w* = 0}",
            "one": "log-odds of 1{w* = 1}",
            "decision": (
                "u scale, kappa-weighted (decision loss); R x O is expected "
                "here through the link, not a mechanism"
            ),
        }[part]
        record["settings"] = {n: r.setting for n, r in found.items()}
        if "full" in found:
            record["friedman_h2_full"] = found["full"].h2
        out[part] = record
    return out
