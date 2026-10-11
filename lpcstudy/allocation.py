"""Allocation rules A0-A5 (and oracle references), the regime map, and their fitting.

Every rule returns a weight on CP for each (state, evaluation draw, horizon),
shape ``(n, E, nH)``. Only deployable information enters A0-A5 at evaluation
time; oracle quantities are used exclusively as training targets on the
construction/calibration splits (leakage rule L2) and by the reference rules
A4o and A*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from scipy.optimize import least_squares, nnls
from sklearn.tree import DecisionTreeRegressor

from .data import sklearn_seed
from .ensemble import EnsembleMoments, EvaluationDraws
from .networks import TrainedNetwork, train_mlp
from .oracle import characteristic_horizon, curvature, excess_mse, hybrid_mse, \
    oracle_weight, realized_horizon
from .statistics import kaplan_meier

RULE_LABELS: dict[str, str] = {
    "A0": "CP alone",
    "A1": "PLP alone",
    "A2": "Global fixed weight",
    "A3": "Error-predictor allocator (Heuer-inspired)",
    "A4": "LPC closed form (deployable)",
    "A5": "LPC regimes (deployable)",
    "A4o": "LPC closed form (oracle seeds)",
    "A*": "Oracle state-optimal weight",
}


@dataclass
class SeedProxy:
    """Deployable seed estimate ``seed_hat^2 = a f^2 + b g^2``.

    ``f`` is an observable feature and ``g`` the scale of the noise floor:

    * analog seed: ``f = R nu_hat`` (FW Lemma 1: the delay-space distance maps
      to state space through the local conditioning of the delay map) and
      ``g = rho nu_hat`` (FW eq. 3.1: the floor is proportional to ``rho nu``);
    * estimation seed: ``f = rho nu_hat`` (Cramer-Rao floor at the estimate) and
      ``g = rho`` (residual estimator error).

    Both terms scale with ``rho``, so a proxy fitted at one noise level applies
    at another. ``(a, b)`` are fitted by least squares on the log scale (the
    weight depends on seed *ratios*, so multiplicative accuracy is what
    matters), initialized by non-negative least squares.

    Notes
    -----
    Two floors here are not data handling (DEF-0001, WU-0002.11, J): the ``1e-6`` under the
    logarithm of the NNLS start is an initial guess, and the ``1e-300`` inside the residual's
    logarithm cannot bind, because every design row is positive (the floor columns are
    ``rho^2 nu^2 > 0`` and ``rho^2 > 0``).
    """

    slope: float
    floor: float

    @classmethod
    def fit(cls, feature_sq: np.ndarray, floor_sq: np.ndarray, seed_sq: np.ndarray
            ) -> "SeedProxy":
        """Fit on construction states.

        Parameters
        ----------
        feature_sq : np.ndarray
            Per-state (median over draws) squared feature ``(n,)``.
        floor_sq : np.ndarray
            Per-state squared floor scale ``(n,)``.
        seed_sq : np.ndarray
            Oracle squared seed per state ``(n,)``.

        Returns
        -------
        SeedProxy
            Fitted proxy.
        """
        scale = np.median(seed_sq)
        design = np.column_stack([feature_sq, floor_sq]) / scale
        coef, _ = nnls(design, seed_sq / scale)
        start = np.log(np.maximum(coef, 1e-6))
        log_seed = np.log(seed_sq / scale)

        def residual(log_coef: np.ndarray) -> np.ndarray:
            return np.log(design @ np.exp(log_coef) + 1e-300) - log_seed

        sol = least_squares(residual, start, loss="soft_l1")
        slope, floor = np.exp(sol.x)
        return cls(slope=float(slope), floor=float(floor))

    def predict(self, feature: np.ndarray, floor_scale: np.ndarray | float) -> np.ndarray:
        """Return the seed estimate."""
        return np.sqrt(self.slope * feature**2 + self.floor * np.square(floor_scale))


@dataclass
class ProfileProxies:
    """The two seed proxies that define the deployable profile.

    Attributes
    ----------
    analog, estimation : SeedProxy
        Proxies of ``epsilon_s`` and ``delta``.
    nu_cap : float
        Winsorization cap of ``nu_hat`` (99th percentile on construction), which
        guards against rare non-converged estimates.
    """

    analog: SeedProxy
    estimation: SeedProxy
    nu_cap: float

    @staticmethod
    def features(distance: np.ndarray, nu_hat: np.ndarray, noise: float, nu_cap: float
                 ) -> dict[str, np.ndarray]:
        """Features and floor scales of both proxies."""
        nu = np.minimum(nu_hat, nu_cap)
        return {"analog_f": distance * nu, "analog_g": noise * nu,
                "est_f": noise * nu, "est_g": np.full_like(nu, noise)}

    @classmethod
    def fit(cls, distance: np.ndarray, nu_hat: np.ndarray, analog_seed: np.ndarray,
            est_seed: np.ndarray, noise: float) -> "ProfileProxies":
        """Fit both proxies on construction states.

        Parameters
        ----------
        distance, nu_hat : np.ndarray
            Recurrence distance and ``nu(s_hat)`` per (state, draw) ``(n, E)``.
        analog_seed, est_seed : np.ndarray
            Oracle seeds per state ``(n,)``.
        noise : float
            Noise level.

        Returns
        -------
        ProfileProxies
            Fitted proxies.
        """
        cap = float(np.quantile(nu_hat, 0.99))
        f = cls.features(distance, nu_hat, noise, cap)
        med = {k: np.median(v**2, axis=1) for k, v in f.items()}
        return cls(analog=SeedProxy.fit(med["analog_f"], med["analog_g"], analog_seed**2),
                   estimation=SeedProxy.fit(med["est_f"], med["est_g"], est_seed**2),
                   nu_cap=cap)

    def seeds(self, ev: EvaluationDraws, noise: float) -> tuple[np.ndarray, np.ndarray]:
        """Deployable ``(eps_hat, delta_hat)``, each ``(n, E)``."""
        f = self.features(ev.distance, ev.est_nu, noise, self.nu_cap)
        return (self.analog.predict(f["analog_f"], f["analog_g"]),
                self.estimation.predict(f["est_f"], f["est_g"]))


NOISE_SENS_FLOOR: float = 1e-2


def deployable_profile(ev: EvaluationDraws, proxies: ProfileProxies, noise: float,
                       steps_per_lyapunov: int) -> np.ndarray:
    """Deployable four-coordinate LPC profile.

    ``F_hat = (ln eps_hat/rho, ln delta_hat/rho, Lambda_hat/lambda_max, ln(N_hat + c))``:
    recurrence (analog seed), observability (estimation seed), dynamical
    instability, and observation-noise sensitivity of analog retrieval
    (``c = NOISE_SENS_FLOOR`` keeps the logarithm finite when retrieval never changes).

    Parameters
    ----------
    ev : EvaluationDraws
        Evaluation draws with deployable features.
    proxies : ProfileProxies
        Seed proxies.
    noise : float
        Noise level ``rho``.
    steps_per_lyapunov : int
        Steps per Lyapunov time (``lambda_max = 1 / steps_per_lyapunov`` per step).

    Returns
    -------
    np.ndarray
        Profile ``(n, E, 4)``.
    """
    eps_hat, delta_hat = proxies.seeds(ev, noise)
    return np.stack([np.log(eps_hat / noise), np.log(delta_hat / noise),
                     ev.growth_proxy * steps_per_lyapunov,
                     np.log(ev.noise_sens + NOISE_SENS_FLOOR)], axis=-1)


def closed_form_weight(eps_sq: np.ndarray, delta_sq: np.ndarray) -> np.ndarray:
    """FW Corollary 1: ``w = delta^2 / (eps^2 + delta^2)``."""
    return delta_sq / np.maximum(eps_sq + delta_sq, 1e-300)


def closed_form_floor_count(eps_sq: np.ndarray, delta_sq: np.ndarray) -> int:
    """Entries on which the ``1e-300`` floor of :func:`closed_form_weight` binds (DEF-0001).

    The floor binds where ``eps^2 + delta^2 < 1e-300``. Under the theory ``eps^2 > 0`` (FW
    Lemma 1), so a nonzero count on oracle seeds (A4o) or on proxies (A4) is a sentinel. NaN
    does not count (``NaN < x`` is False); it propagates to the weight.

    Parameters
    ----------
    eps_sq, delta_sq : np.ndarray
        Squared seeds, any common shape.

    Returns
    -------
    int
        Number of entries with ``eps_sq + delta_sq < 1e-300``.
    """
    return int(np.sum(eps_sq + delta_sq < 1e-300))


def nu_cap_clip_count(est_nu: np.ndarray, nu_cap: float) -> int:
    """Estimates that the winsorization cap of :class:`ProfileProxies` changes (``nu_cap_clips``).

    ``features`` takes ``np.minimum(nu_hat, nu_cap)``, which changes exactly the entries with
    ``nu_hat > nu_cap`` (strict: an entry equal to the cap is not clipped). On construction the
    cap is the 99th percentile, so about 1% (exactly ``ceil(0.01 (N - 1))`` without ties) are
    clipped by construction; on other splits the rate is a diagnostic.

    Parameters
    ----------
    est_nu : np.ndarray
        ``nu_hat`` per (state, draw), any shape.
    nu_cap : float
        The cap of the fitted proxies.

    Returns
    -------
    int
        Number of entries above the cap.
    """
    return int(np.sum(est_nu > nu_cap))


def constant_target_count(w_target: np.ndarray, log_t_target: np.ndarray) -> int:
    """Targets of :func:`fit_regime_tree` whose standard deviation is below its ``1e-12`` guard.

    The tree standardizes each target by ``std + 1e-12``. A constant target (std 0, or round-off
    of order 1e-16) is then divided by the guard instead of its spread; this counts the columns
    (0 to 2) for which the guard is larger than the spread. The targets do not depend on ``K``,
    so the caller counts once per fit (D7).

    Parameters
    ----------
    w_target, log_t_target : np.ndarray
        The two per-state targets, ``(n,)``.

    Returns
    -------
    int
        0, 1 or 2.
    """
    targets = np.column_stack([w_target, log_t_target])
    return int(np.sum(targets.std(axis=0) < 1e-12))


def pooled_floor_count(moments: EnsembleMoments, members: np.ndarray | None = None) -> int:
    """Horizons at which a pooled curvature is below the ``1e-300`` floor (A2, regime weights).

    The pool is all states (A2, :func:`global_weight`) or the given members
    (:func:`regime_weight`); the denominator is ``sum_i c_i`` per horizon, the expression of
    those functions. Under P1(a) every ``c_i >= rho^2 / k > 0``, so a nonzero count is a
    sentinel.

    Parameters
    ----------
    moments : EnsembleMoments
        Oracle moments, arrays ``(n, nH)``.
    members : np.ndarray, optional
        State indices of the pool (default: all states).

    Returns
    -------
    int
        Number of horizons with ``sum c < 1e-300``.
    """
    curv = curvature(moments)
    denominator = np.sum(curv if members is None else curv[np.asarray(members)], axis=0)
    return int(np.sum(denominator < 1e-300))


@dataclass
class ErrorPredictor:
    """Heuer-inspired allocator: learned per-forecaster error magnitudes.

    Heuer et al. (2026) attach to the ML component a second output that
    predicts its own loss and blend ML and physics by a ramp on that predicted
    error. With two forecasters, the adaptation predicts ``log e^2`` for both
    CP and PLP from the raw delay vector and combines them by inverse expected
    squared error, ``w = e_P^2 / (e_C^2 + e_P^2)`` (Bates-Granger weighting
    with learned, state-dependent error variances).

    ``weights`` clips the log ratio of the two predicted errors to ``+-50`` before ``exp``: an
    overflow guard that changes the weight by less than ``2e-22`` and so is not counted
    (DEF-0001, WU-0002.11, J).
    """

    network: TrainedNetwork
    grid: np.ndarray

    @classmethod
    def fit(cls, inputs: np.ndarray, cp_err: np.ndarray, plp_err: np.ndarray,
            grid: np.ndarray, noise: float, width: int, epochs: int, seed: int
            ) -> "ErrorPredictor":
        """Train on construction states x retained oracle draws.

        Parameters
        ----------
        inputs : np.ndarray
            Noisy delay vectors ``(n, K, D)``.
        cp_err, plp_err : np.ndarray
            Realized errors at ``grid`` ``(n, K, nG)``.
        grid : np.ndarray
            Horizons of the outputs.
        noise : float
            Noise level (sets the log floor ``(0.1 rho)^2``).
        width : int
            Hidden width.
        epochs : int
            Epochs.
        seed : int
            Seed.

        Returns
        -------
        ErrorPredictor
            Trained allocator.
        """
        floor = (0.1 * noise) ** 2
        targets = np.concatenate([np.log(cp_err**2 + floor), np.log(plp_err**2 + floor)],
                                 axis=-1)
        net = train_mlp(inputs.reshape(-1, inputs.shape[-1]),
                        targets.reshape(-1, targets.shape[-1]), width, epochs, seed)
        return cls(network=net, grid=np.asarray(grid))

    def weights(self, inputs: np.ndarray, horizons: np.ndarray) -> np.ndarray:
        """Weights on CP at ``horizons`` for inputs ``(n, E, D)``."""
        pred = np.asarray(self.network.predict(inputs.reshape(-1, inputs.shape[-1])))
        n_grid = len(self.grid)
        log_cp, log_plp = pred[:, :n_grid], pred[:, n_grid:]
        interp = lambda logs: np.stack([np.interp(horizons, self.grid, row)
                                        for row in logs])
        diff = interp(log_cp) - interp(log_plp)  # log(e_C^2 / e_P^2)
        weight = 1.0 / (1.0 + np.exp(np.clip(diff, -50, 50)))
        return weight.reshape(*inputs.shape[:2], len(horizons))


def global_weight(moments: EnsembleMoments) -> np.ndarray:
    """A2: pooled minimizer of mean squared error per horizon, ``(nH,)``."""
    numer = np.sum(moments.sq_plp - moments.cross, axis=0)
    denom = np.sum(curvature(moments), axis=0)
    return np.clip(numer / np.maximum(denom, 1e-300), 0.0, 1.0)


def state_horizon_target(moments: EnsembleMoments, noise: float, theta: float
                         ) -> np.ndarray:
    """Characteristic horizon (steps) of the oracle hybrid, per state (censored at ``H_max``)."""
    mse = hybrid_mse(moments, oracle_weight(moments))
    horizon, _ = characteristic_horizon(mse, moments.horizons, noise, theta)
    return horizon


@dataclass
class RegimeMap:
    """Regression-tree abstraction ``F_hat -> k -> (w_k(H), T_k)``.

    Attributes
    ----------
    tree : DecisionTreeRegressor
        Tree fitted on the construction split.
    leaf_ids : np.ndarray
        Leaf node ids; regime ``k`` is ``leaf_ids[k]``.
    weights : np.ndarray
        Optimal regime weights ``(K, nH)`` from the calibration split (Theorem P3(a)).
    horizons_km : np.ndarray
        Kaplan-Meier median horizon per regime (steps; ``nan`` if not reached).
    empty : np.ndarray or None
        Boolean ``(K,)``: regime ``k`` had no calibration (state, draw), so its weights are the
        ``fallback`` row (A2) and its Kaplan-Meier horizon is NaN (``empty_regime_fallback``).
        ``None`` for hand-built maps.
    pooled_curvature_floor : int
        Number of (regime, horizon) pools whose summed curvature was below the ``1e-300``
        floor of :func:`regime_weight` (a sentinel; 0 for hand-built maps).
    """

    tree: DecisionTreeRegressor
    leaf_ids: np.ndarray
    weights: np.ndarray
    horizons_km: np.ndarray
    empty: np.ndarray | None = None
    pooled_curvature_floor: int = 0

    @property
    def n_regimes(self) -> int:
        """Number of regimes ``K``."""
        return len(self.leaf_ids)

    def assign(self, profile: np.ndarray) -> np.ndarray:
        """Regime index for profiles ``(..., 3)``."""
        leaves = self.tree.apply(profile.reshape(-1, profile.shape[-1]))
        return np.searchsorted(self.leaf_ids, leaves).reshape(profile.shape[:-1])


def fit_regime_tree(profile: np.ndarray, w_target: np.ndarray, log_t_target: np.ndarray,
                    n_regimes: int, seed: int) -> DecisionTreeRegressor:
    """Two-output CART on the deployable profile (construction split).

    Parameters
    ----------
    profile : np.ndarray
        Profiles ``(n, E, p)``.
    w_target : np.ndarray
        State-optimal weight at ``H_ref`` per state ``(n,)``.
    log_t_target : np.ndarray
        Log characteristic horizon per state ``(n,)``.
    n_regimes : int
        Number of leaves ``K``.
    seed : int
        Seed.

    Returns
    -------
    DecisionTreeRegressor
        Fitted tree (targets standardized so both outputs count equally).
    """
    n_states, n_draws, _ = profile.shape
    targets = np.column_stack([w_target, log_t_target])
    targets = (targets - targets.mean(axis=0)) / (targets.std(axis=0) + 1e-12)
    tree = DecisionTreeRegressor(max_leaf_nodes=n_regimes,
                                 min_samples_leaf=max(10, n_states * n_draws // 50),
                                 random_state=sklearn_seed(seed, "regime-tree"))
    tree.fit(profile.reshape(-1, profile.shape[-1]), np.repeat(targets, n_draws, axis=0))
    return tree


def regime_weight(moments: EnsembleMoments, members: np.ndarray) -> np.ndarray:
    """Optimal common weight of a set of (state, draw) pairs (Theorem P3(a)), per horizon.

    The mean excess error over the members is ``sum_i c_i (w - u_i)^2 / n + const``, a
    strictly convex quadratic in ``w`` with vertex ``sum_i c_i u_i / sum_i c_i`` over the
    *unclipped* per-state optima ``u_i = b_i / c_i``. Its minimizer on ``[0, 1]`` is the
    projection of the vertex: sum first, then clip,
    ``w_S = clip(sum_i b_i / sum_i c_i, 0, 1)`` with ``b_i = E[e_P (e_P - e_C)]`` and
    ``c_i = E[(e_C - e_P)^2]`` of state ``i``. The mean of the clipped ``w*_i``
    weighted by ``c_i`` is not this minimizer (DEF-0003). The denominator keeps the
    ``1e-300`` floor of ``oracle_weight`` (it cannot bind under P1(a), where
    ``c >= rho^2 / k``; counting it belongs to DEF-0001).

    Parameters
    ----------
    moments : EnsembleMoments
        Oracle moments of the states, arrays ``(n, nH)``.
    members : np.ndarray
        State indices of the (state, draw) pairs of the regime, ``(m,)``. A state
        appears once per draw that falls in the regime.

    Returns
    -------
    np.ndarray
        Weights ``(nH,)``.

    Raises
    ------
    ValueError
        If ``members`` is empty.
    """
    members = np.asarray(members)
    if members.size == 0:
        raise ValueError("regime_weight needs at least one member")
    numerator = np.sum((moments.sq_plp - moments.cross)[members], axis=0)
    denominator = np.sum(curvature(moments)[members], axis=0)
    return np.clip(numerator / np.maximum(denominator, 1e-300), 0.0, 1.0)


def calibrate_regimes(tree: DecisionTreeRegressor, profile: np.ndarray,
                      moments: EnsembleMoments, ev: EvaluationDraws, theta: float,
                      fallback: np.ndarray) -> RegimeMap:
    """Regime weights (optimal per regime, Theorem P3(a)) and KM horizons on calibration.

    Parameters
    ----------
    tree : DecisionTreeRegressor
        Fitted tree.
    profile : np.ndarray
        Calibration profiles ``(n, E, 3)``.
    moments : EnsembleMoments
        Calibration oracle moments (horizons must match ``ev.horizons``).
    ev : EvaluationDraws
        Calibration evaluation draws (for realized horizons).
    theta : float
        Tolerance for regime horizons.
    fallback : np.ndarray
        Weights ``(nH,)`` for a regime with no calibration states.

    Notes
    -----
    The Kaplan-Meier horizon is computed only when the horizons are contiguous from 1. This
    function sees only the core cells, whose horizons are ``1..H_max`` (``fit_rules``), so the
    branch always runs here (DEF-0001, WU-0002.11, J: not a silent skip).

    Returns
    -------
    RegimeMap
        Calibrated regime map; ``empty`` marks the regimes that fell back to ``fallback``
        (with NaN Kaplan-Meier horizon), and ``pooled_curvature_floor`` counts the floored
        pools. Neither changes a weight.
    """
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    leaves = tree.apply(profile.reshape(-1, profile.shape[-1])).reshape(profile.shape[:2])
    regime = np.searchsorted(leaf_ids, leaves)
    n_regimes = len(leaf_ids)
    weights = np.tile(fallback, (n_regimes, 1)).astype(float)
    horizons_km = np.full(n_regimes, np.nan)
    empty = np.zeros(n_regimes, dtype=bool)
    pooled_floor = 0
    for k in range(n_regimes):
        state_idx, draw_idx = np.nonzero(regime == k)
        if state_idx.size == 0:
            empty[k] = True
            continue
        pooled_floor += pooled_floor_count(moments, state_idx)
        weights[k] = regime_weight(moments, state_idx)
        if np.array_equal(ev.horizons, np.arange(1, len(ev.horizons) + 1)):
            err = weights[k] * ev.cp_err[state_idx, draw_idx] + \
                (1 - weights[k]) * ev.plp_err[state_idx, draw_idx] - \
                ev.verify_noise[state_idx, draw_idx]
            dur, event = realized_horizon(err, ev.horizons, theta)
            horizons_km[k] = kaplan_meier(dur, event, len(ev.horizons)).median()
    return RegimeMap(tree=tree, leaf_ids=leaf_ids, weights=weights,
                     horizons_km=horizons_km, empty=empty, pooled_curvature_floor=pooled_floor)


def regime_regret(regime_map: RegimeMap, profile: np.ndarray, moments: EnsembleMoments,
                  column: int) -> tuple[float, float]:
    """Mean abstraction regret and its ratio to the best-single error variance.

    Parameters
    ----------
    regime_map : RegimeMap
        Regime map.
    profile : np.ndarray
        Profiles ``(n, E, 3)``.
    moments : EnsembleMoments
        Oracle moments of the same states.
    column : int
        Horizon column.

    Returns
    -------
    tuple[float, float]
        Mean exact excess error ``V(w_k) - V(w*)`` (Theorem P1(a); it equals
        ``c (w_k - w*)^2`` only for states with ``w*`` unclipped) and its ratio to
        the mean ``min(E e_C^2, E e_P^2)`` (the definition of the best single forecaster per
        state, not a guard; DEF-0001, J).
    """
    regime = regime_map.assign(profile)
    w_k = regime_map.weights[regime, column]  # (n, E)
    # Only the three second moments enter ``excess_mse``; slice them to one column.
    one_column = replace(moments, horizons=moments.horizons[column:column + 1],
                         sq_cp=moments.sq_cp[:, column:column + 1],
                         sq_plp=moments.sq_plp[:, column:column + 1],
                         cross=moments.cross[:, column:column + 1])
    regret = float(np.mean(excess_mse(one_column, w_k[:, :, None])))
    best = float(np.mean(np.minimum(moments.sq_cp[:, column], moments.sq_plp[:, column])))
    return regret, regret / best
