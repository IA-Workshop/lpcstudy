"""Allocation rules A0-A5: how much weight to put on each forecaster.

The study blends two forecasts: CP (the analog forecaster, which copies the
future of the most similar past state) and PLP (the physics forecaster, which
estimates the current state and runs the model forward). A blend is
``w * CP + (1 - w) * PLP``, and an *allocation rule* chooses the weight ``w``
for each state and each forecast horizon (steps ahead). Every rule here
returns weights of shape ``(n, E, nH)``: ``n`` states, ``E`` evaluation
draws and ``nH`` horizons.

The rules are A0 (CP alone), A1 (PLP alone), A2 (one global weight), A3 (a
learned error predictor), A4 (the closed-form weight built from the four
local predictability conditions) and A5 (a few regimes found by a decision
tree). The oracle rules A4o and A* use quantities that a real forecaster
could not know, so they only serve as references.

Leakage rule L2: oracle quantities (computed from the true state) are used
only as training targets on the construction and calibration splits. At
evaluation time A0-A5 see only deployable information.

This module is fed by ``ensemble`` (moments and evaluation draws) and
``oracle`` (the exact optimal weights), and is called by ``pipeline`` (which
fits and scores the rules) and ``analysis`` (which tests the hypotheses).
Read ``ensemble`` and ``oracle`` first for the meaning of the moments.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from scipy.optimize import least_squares, nnls
from sklearn.tree import DecisionTreeRegressor

from .data import sklearn_seed
from .ensemble import EnsembleMoments, EvaluationDraws
from .networks import TrainedNetwork, train_mlp
from .oracle import (
    characteristic_horizon,
    curvature,
    excess_mse,
    hybrid_mse,
    oracle_weight,
    realized_horizon,
)
from .provenance import index_digest
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


def log_scale_fit(
    columns: list[np.ndarray], seed_sq: np.ndarray
) -> tuple[np.ndarray, int, int]:
    """Fit ``seed^2 ~ sum_j c_j columns[j]`` by robust log-scale least squares.

    This is the fit of :class:`SeedProxy` (v3 section 5), for any number of
    non-negative terms. The coefficients are ``c = exp(x)``, so they stay
    positive; ``x`` minimizes the ``soft_l1`` loss of the residuals
    ``ln(sum_j c_j columns[j]) - ln(seed^2)``, both sides divided by the median
    of ``seed^2``. The start is the non-negative least squares solution,
    floored at ``1e-6`` under its logarithm (a starting value, not data
    handling). With the two columns of a proxy it is the long-standing fit
    (same operations, so bitwise the same result); with one column it is the
    refit of a proxy with one term removed (WU-0039b, ablation (a)).

    A coefficient whose term the data do not support is driven towards 0,
    which ``exp(x)`` reaches only in the limit, so it comes out as a small
    positive number (1e-16 to 1e-7 in WU-0036), not as an exact 0.

    Parameters
    ----------
    columns : list[np.ndarray]
        Design columns, each of shape ``(n,)`` and positive.
    seed_sq : np.ndarray
        Oracle squared seed per state, shape ``(n,)``.

    Returns
    -------
    tuple[np.ndarray, int, int]
        The coefficients (shape ``(len(columns),)``), and the ``nfev`` and
        ``status`` of the ``least_squares`` call.
    """
    scale = np.median(seed_sq)
    design = np.column_stack(columns) / scale
    coef, _ = nnls(design, seed_sq / scale)
    start = np.log(np.maximum(coef, 1e-6))
    log_seed = np.log(seed_sq / scale)

    def residual(log_coef: np.ndarray) -> np.ndarray:
        return np.log(design @ np.exp(log_coef) + 1e-300) - log_seed

    sol = least_squares(residual, start, loss="soft_l1")
    return np.exp(sol.x), int(sol.nfev), int(sol.status)


@dataclass
class SeedProxy:
    """A deployable estimate of a "seed" (an error source) from observables.

    The seed estimate is ``seed_hat^2 = a f^2 + b g^2``. Here ``f`` is a
    feature we can compute from data and ``g`` is the scale of the noise
    floor. The two kinds of seed use different features:

    * analog seed: ``f = R nu_hat`` (FW Lemma 1: the distance to the nearest
      analog in delay space maps to state space through the local
      conditioning of the delay map) and ``g = rho nu_hat`` (FW eq. 3.1: the
      floor is proportional to ``rho nu``);
    * estimation seed: ``f = rho nu_hat`` (the Cramer-Rao floor, the smallest
      error any unbiased estimator can reach, evaluated at the estimate) and
      ``g = rho`` (the leftover estimator error).

    Both terms scale with ``rho`` (the noise level), so a proxy fitted at one
    noise level also applies at another. The coefficients ``(a, b)`` are
    fitted by least squares on the log scale. The blend weight depends on
    seed *ratios*, so being accurate in relative terms is what matters. The
    fit starts from a non-negative least squares solution.

    Notes
    -----
    Two floors here are not data handling (DEF-0001, WU-0002.11, J): the
    ``1e-6`` under the logarithm of the starting guess is only an initial
    value, and the ``1e-300`` inside the residual's logarithm can never bind,
    because every design row is positive (the floor columns are
    ``rho^2 nu^2 > 0`` and ``rho^2 > 0``).

    ``nfev`` and ``status`` are the number of function evaluations and the
    termination status of the ``least_squares`` call (scipy's
    ``OptimizeResult``; 1 to 4 mean a tolerance was met, 0 means the
    evaluation limit was hit). They record where the fit stopped (WU-0003.7a:
    a flipped stopping test moves a coefficient by up to about
    ``sqrt(ftol)``), change no coefficient, and are ``None`` for a hand-built
    proxy that was not fitted.
    """

    slope: float
    floor: float
    nfev: int | None = None
    status: int | None = None

    @classmethod
    def fit(
        cls,
        feature_sq: np.ndarray,
        floor_sq: np.ndarray,
        seed_sq: np.ndarray,
    ) -> "SeedProxy":
        """Fit the two coefficients on the construction states.

        Parameters
        ----------
        feature_sq : np.ndarray
            Per-state squared feature (median over draws), shape ``(n,)``.
        floor_sq : np.ndarray
            Per-state squared floor scale, shape ``(n,)``.
        seed_sq : np.ndarray
            Oracle squared seed per state, shape ``(n,)``.

        Returns
        -------
        SeedProxy
            The fitted proxy.
        """
        (slope, floor), nfev, status = log_scale_fit(
            [feature_sq, floor_sq], seed_sq
        )
        return cls(
            slope=float(slope),
            floor=float(floor),
            nfev=nfev,
            status=status,
        )

    def predict(
        self, feature: np.ndarray, floor_scale: np.ndarray | float
    ) -> np.ndarray:
        """Return the seed estimate for the given feature and floor scale."""
        return np.sqrt(
            self.slope * feature**2 + self.floor * np.square(floor_scale)
        )


@dataclass
class ProfileProxies:
    """The two seed proxies that define the deployable profile.

    Attributes
    ----------
    analog, estimation : SeedProxy
        Proxies of ``epsilon_s`` (the analog seed) and ``delta`` (the
        estimation seed).
    nu_cap : float
        Winsorization cap of ``nu_hat`` (the 99th percentile on the
        construction split). Winsorizing means replacing values above the
        cap by the cap, which guards against rare estimates that did not
        converge.
    """

    analog: SeedProxy
    estimation: SeedProxy
    nu_cap: float

    @staticmethod
    def features(
        distance: np.ndarray,
        nu_hat: np.ndarray,
        noise: float,
        nu_cap: float,
    ) -> dict[str, np.ndarray]:
        """Return the features and floor scales of both proxies."""
        nu = np.minimum(nu_hat, nu_cap)
        return {
            "analog_f": distance * nu,
            "analog_g": noise * nu,
            "est_f": noise * nu,
            "est_g": np.full_like(nu, noise),
        }

    @classmethod
    def fit(
        cls,
        distance: np.ndarray,
        nu_hat: np.ndarray,
        analog_seed: np.ndarray,
        est_seed: np.ndarray,
        noise: float,
    ) -> "ProfileProxies":
        """Fit both proxies on the construction states.

        Parameters
        ----------
        distance, nu_hat : np.ndarray
            Recurrence distance and ``nu(s_hat)`` per (state, draw), shape
            ``(n, E)``.
        analog_seed, est_seed : np.ndarray
            Oracle seeds per state, shape ``(n,)``.
        noise : float
            Noise level.

        Returns
        -------
        ProfileProxies
            The fitted proxies.
        """
        cap = float(np.quantile(nu_hat, 0.99))
        f = cls.features(distance, nu_hat, noise, cap)
        med = {k: np.median(v**2, axis=1) for k, v in f.items()}
        return cls(
            analog=SeedProxy.fit(
                med["analog_f"], med["analog_g"], analog_seed**2
            ),
            estimation=SeedProxy.fit(med["est_f"], med["est_g"], est_seed**2),
            nu_cap=cap,
        )

    def seeds(
        self, ev: EvaluationDraws, noise: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return the deployable ``(eps_hat, delta_hat)``, each ``(n, E)``."""
        f = self.features(ev.distance, ev.est_nu, noise, self.nu_cap)
        return (
            self.analog.predict(f["analog_f"], f["analog_g"]),
            self.estimation.predict(f["est_f"], f["est_g"]),
        )


NOISE_SENS_FLOOR: float = 1e-2


def deployable_profile(
    ev: EvaluationDraws,
    proxies: ProfileProxies,
    noise: float,
    steps_per_lyapunov: int,
) -> np.ndarray:
    """Build the deployable four-number LPC profile of each state.

    The profile ``F_hat`` is
    ``(ln eps_hat/rho, ln delta_hat/rho, Lambda_hat/lambda_max,
    ln(N_hat + c))``. In words, the four local predictability conditions are
    recurrence (the analog seed), observability (the estimation seed),
    dynamical instability (how fast nearby states separate), and the
    sensitivity of analog retrieval to observation noise. The constant
    ``c = NOISE_SENS_FLOOR`` keeps the last logarithm finite when retrieval
    never changes.

    Parameters
    ----------
    ev : EvaluationDraws
        Evaluation draws with deployable features.
    proxies : ProfileProxies
        Seed proxies.
    noise : float
        Noise level ``rho``.
    steps_per_lyapunov : int
        Steps per Lyapunov time (``lambda_max = 1 / steps_per_lyapunov`` per
        step).

    Returns
    -------
    np.ndarray
        Profile, shape ``(n, E, 4)``.
    """
    eps_hat, delta_hat = proxies.seeds(ev, noise)
    return np.stack(
        [
            np.log(eps_hat / noise),
            np.log(delta_hat / noise),
            ev.growth_proxy * steps_per_lyapunov,
            np.log(ev.noise_sens + NOISE_SENS_FLOOR),
        ],
        axis=-1,
    )


def closed_form_weight(eps_sq: np.ndarray, delta_sq: np.ndarray) -> np.ndarray:
    """Return the closed-form weight on CP (FW Corollary 1).

    The weight is ``w = delta^2 / (eps^2 + delta^2)``: the more accurate CP
    is (small ``eps``, the analog seed), the more weight it gets.
    """
    return delta_sq / np.maximum(eps_sq + delta_sq, 1e-300)


def closed_form_floor_count(eps_sq: np.ndarray, delta_sq: np.ndarray) -> int:
    """Count the entries where the ``1e-300`` floor of the weight binds.

    The floor in :func:`closed_form_weight` binds where
    ``eps^2 + delta^2 < 1e-300`` (DEF-0001). Under the theory ``eps^2 > 0``
    (FW Lemma 1), so a nonzero count on oracle seeds (A4o) or on proxies (A4)
    is a warning sign. A NaN does not count (``NaN < x`` is False); it
    propagates to the weight instead.

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
    """Count the estimates changed by the cap of :class:`ProfileProxies`.

    ``ProfileProxies.features`` takes ``np.minimum(nu_hat, nu_cap)``, which
    changes exactly the entries with ``nu_hat > nu_cap`` (strictly greater:
    an entry equal to the cap is not changed). On the construction split the
    cap is the 99th percentile, so about 1% of the entries are changed by
    construction (exactly ``ceil(0.01 (N - 1))`` when there are no ties). On
    other splits the rate is only a diagnostic. The result is reported as
    ``nu_cap_clips``.

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


def constant_target_count(
    w_target: np.ndarray, log_t_target: np.ndarray
) -> int:
    """Count the tree targets whose spread is below the ``1e-12`` guard.

    :func:`fit_regime_tree` standardizes each target by ``std + 1e-12``. A
    constant target (standard deviation 0, or round-off of order 1e-16) is
    then divided by the guard instead of its spread. This counts the columns
    (0 to 2) for which the guard is larger than the spread. The targets do
    not depend on the number of regimes ``K``, so the caller counts once per
    fit (D7).

    Parameters
    ----------
    w_target, log_t_target : np.ndarray
        The two per-state targets, each of shape ``(n,)``.

    Returns
    -------
    int
        0, 1 or 2.
    """
    targets = np.column_stack([w_target, log_t_target])
    return int(np.sum(targets.std(axis=0) < 1e-12))


def _pooled_sums(
    moments: EnsembleMoments, members: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(sum b, sum c)`` per horizon over a pool of states.

    Here ``b = E[e_P (e_P - e_C)]`` and ``c = E[(e_C - e_P)^2]`` are the
    per-state moments (the second is the "curvature"). With ``members=None``
    the pool is every state; otherwise it is the listed state indices.
    """
    rows = slice(None) if members is None else np.asarray(members)
    numerator = np.sum((moments.sq_plp - moments.cross)[rows], axis=0)
    denominator = np.sum(curvature(moments)[rows], axis=0)
    return numerator, denominator


def pooled_floor_count(
    moments: EnsembleMoments, members: np.ndarray | None = None
) -> int:
    """Count horizons where a pooled curvature is below the ``1e-300`` floor.

    This applies to A2 (:func:`global_weight`, all states) and to the regime
    weights (:func:`regime_weight`, the given members). The denominator is
    ``sum_i c_i`` per horizon, the same expression those functions use.
    The pooled weight divides by that sum, so a sum below the floor would
    leave the weight undefined at that horizon. No per-state lower bound on
    ``c_i`` is claimed: a bound such as ``c_i >= rho^2 / k`` needs the
    expectation to include the library noise, a hypothesis not established
    here, and the smallest per-state curvature in the DEV-2 prototype data
    is ``0.012 rho^2`` (DEF-0030). A nonzero count is a warning sign.

    Parameters
    ----------
    moments : EnsembleMoments
        Oracle moments, arrays of shape ``(n, nH)``.
    members : np.ndarray, optional
        State indices of the pool (default: all states).

    Returns
    -------
    int
        Number of horizons with ``sum c < 1e-300``.
    """
    _, denominator = _pooled_sums(moments, members)
    return int(np.sum(denominator < 1e-300))


@dataclass
class ErrorPredictor:
    """A3, the Heuer-inspired allocator: learned error sizes of each forecaster.

    Heuer et al. (2026) give the machine-learning component a second output
    that predicts its own loss, and they blend the ML and physics forecasts
    with a ramp on that predicted error. With two forecasters, the adaptation
    here predicts ``log e^2`` (the log of the squared error) for both CP and
    PLP from the raw delay vector, and combines them by inverse expected
    squared error, ``w = e_P^2 / (e_C^2 + e_P^2)``. This is Bates-Granger
    weighting with learned, state-dependent error variances.

    ``weights`` clips the log ratio of the two predicted errors to ``+-50``
    before ``exp``. That is an overflow guard which changes the weight by less
    than ``2e-22``, so it is not counted (DEF-0001, WU-0002.11, J).
    """

    network: TrainedNetwork
    grid: np.ndarray

    @classmethod
    def fit(
        cls,
        inputs: np.ndarray,
        cp_err: np.ndarray,
        plp_err: np.ndarray,
        grid: np.ndarray,
        noise: float,
        width: int,
        epochs: int,
        rng: np.random.Generator,
    ) -> "ErrorPredictor":
        """Train on construction states and their retained oracle draws.

        Parameters
        ----------
        inputs : np.ndarray
            Noisy delay vectors, shape ``(n, K, D)``.
        cp_err, plp_err : np.ndarray
            Realized errors at ``grid``, shape ``(n, K, nG)``.
        grid : np.ndarray
            Horizons of the network outputs.
        noise : float
            Noise level (it sets the log floor ``(0.1 rho)^2``).
        width : int
            Hidden width of the network.
        epochs : int
            Number of training epochs.
        rng : np.random.Generator
            Randomness for the network (see ``networks.train_mlp``). The
            caller builds it from ``make_rng(seed, system, embed_dim,
            "allocator")``. Needs owner review before freeze.

        Returns
        -------
        ErrorPredictor
            The trained allocator.
        """
        floor = (0.1 * noise) ** 2
        targets = np.concatenate(
            [np.log(cp_err**2 + floor), np.log(plp_err**2 + floor)], axis=-1
        )
        net = train_mlp(
            inputs.reshape(-1, inputs.shape[-1]),
            targets.reshape(-1, targets.shape[-1]),
            width,
            epochs,
            rng,
        )
        return cls(network=net, grid=np.asarray(grid))

    def weights(self, inputs: np.ndarray, horizons: np.ndarray) -> np.ndarray:
        """Return the weights on CP at ``horizons`` for inputs ``(n, E, D)``."""
        pred = np.asarray(
            self.network.predict(inputs.reshape(-1, inputs.shape[-1]))
        )
        n_grid = len(self.grid)
        log_cp, log_plp = pred[:, :n_grid], pred[:, n_grid:]

        def interp(logs: np.ndarray) -> np.ndarray:
            return np.stack(
                [np.interp(horizons, self.grid, row) for row in logs]
            )

        diff = interp(log_cp) - interp(log_plp)  # log(e_C^2 / e_P^2)
        weight = 1.0 / (1.0 + np.exp(np.clip(diff, -50, 50)))
        return weight.reshape(*inputs.shape[:2], len(horizons))


def _pooled_weight(
    moments: EnsembleMoments, members: np.ndarray | None = None
) -> np.ndarray:
    """Return the clipped pooled minimizer ``clip(sum b / sum c, 0, 1)``."""
    numerator, denominator = _pooled_sums(moments, members)
    return np.clip(numerator / np.maximum(denominator, 1e-300), 0.0, 1.0)


def global_weight(moments: EnsembleMoments) -> np.ndarray:
    """A2: the single weight that minimizes the pooled error, per horizon.

    The result has shape ``(nH,)``: one weight for every state, chosen
    separately at each horizon.
    """
    return _pooled_weight(moments)


def state_horizon_target(
    moments: EnsembleMoments, noise: float, theta: float
) -> np.ndarray:
    """Return the oracle hybrid's characteristic horizon (steps) per state.

    The characteristic horizon is the first horizon at which the error of the
    best possible blend exceeds the tolerance ``theta``. It is censored at
    ``H_max`` (the largest horizon) when the tolerance is never exceeded.
    """
    mse = hybrid_mse(moments, oracle_weight(moments))
    horizon, _ = characteristic_horizon(mse, moments.horizons, noise, theta)
    return horizon


@dataclass
class RegimeMap:
    """A5: a regression tree that sorts profiles into regimes.

    The map goes ``F_hat -> k -> (w_k(H), T_k)``: a profile is assigned to a
    regime ``k``, and each regime has one weight per horizon and one median
    horizon.

    Attributes
    ----------
    tree : DecisionTreeRegressor
        Tree fitted on the construction split.
    leaf_ids : np.ndarray
        Leaf node ids; regime ``k`` is ``leaf_ids[k]``.
    weights : np.ndarray
        Optimal regime weights, shape ``(K, nH)``, from the calibration split
        (Theorem P3(a)).
    horizons_km : np.ndarray
        Kaplan-Meier median horizon per regime (steps; ``nan`` if the median
        is not reached).
    empty : np.ndarray or None
        Boolean ``(K,)``. True where regime ``k`` had no calibration (state,
        draw), so its weights are the ``fallback`` row (A2) and its
        Kaplan-Meier horizon is NaN (``empty_regime_fallback``). ``None`` for
        hand-built maps.
    pooled_curvature_floor : int
        Number of (regime, horizon) pools whose summed curvature was below the
        ``1e-300`` floor of :func:`regime_weight` (a warning sign; 0 for
        hand-built maps).
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
        """Return the regime index for profiles of shape ``(..., 3)``."""
        leaves = self.tree.apply(profile.reshape(-1, profile.shape[-1]))
        return np.searchsorted(self.leaf_ids, leaves).reshape(
            profile.shape[:-1]
        )

    def leaf_digest(self, *profiles: np.ndarray) -> str:
        """Return a SHA-256 fingerprint of the leaf of every (state, draw).

        The leaf ids are ``tree.apply`` of each array (``(n, E, p)`` is
        flattened to ``(n E, p)`` in C order), concatenated in the order given
        and hashed by :func:`lpcstudy.provenance.index_digest` as int64. A
        change of one state's leaf, or of the order of the arrays, changes the
        digest. It only reads the fitted tree: no random number, and no change
        to the tree or the profiles (WU-0003.7a; it records the A5 leaf
        membership of the calibration and test states so two runs can be
        compared).

        Parameters
        ----------
        *profiles : np.ndarray
            Profile arrays of shape ``(n, E, p)``, for example the calibration
            and then the test profiles.

        Returns
        -------
        str
            64 lowercase hexadecimal characters.
        """
        leaves = [self.tree.apply(p.reshape(-1, p.shape[-1])) for p in profiles]
        return index_digest(np.concatenate(leaves))


def fit_regime_tree(
    profile: np.ndarray,
    w_target: np.ndarray,
    log_t_target: np.ndarray,
    n_regimes: int,
    seed: int,
) -> DecisionTreeRegressor:
    """Fit a two-output CART tree on the deployable profile.

    CART is a decision tree that splits the profile space greedily. The tree
    is fitted on the construction split only.

    Parameters
    ----------
    profile : np.ndarray
        Profiles, shape ``(n, E, p)``.
    w_target : np.ndarray
        State-optimal weight at ``H_ref`` per state, shape ``(n,)``.
    log_t_target : np.ndarray
        Log characteristic horizon per state, shape ``(n,)``.
    n_regimes : int
        Number of leaves ``K``.
    seed : int
        Study seed (the tree's own seed is derived from it).

    Returns
    -------
    DecisionTreeRegressor
        The fitted tree. Both targets are standardized so that they count
        equally.
    """
    n_states, n_draws, _ = profile.shape
    targets = np.column_stack([w_target, log_t_target])
    targets = (targets - targets.mean(axis=0)) / (targets.std(axis=0) + 1e-12)
    tree = DecisionTreeRegressor(
        max_leaf_nodes=n_regimes,
        min_samples_leaf=max(10, n_states * n_draws // 50),
        random_state=sklearn_seed(seed, "regime-tree"),
    )
    tree.fit(
        profile.reshape(-1, profile.shape[-1]),
        np.repeat(targets, n_draws, axis=0),
    )
    return tree


def regime_weight(moments: EnsembleMoments, members: np.ndarray) -> np.ndarray:
    """Return the optimal common weight of a regime, per horizon.

    This is Theorem P3(a). The mean excess error over the members is
    ``sum_i c_i (w - u_i)^2 / n + const``, a strictly convex quadratic in
    ``w`` whose vertex is ``sum_i c_i u_i / sum_i c_i``, built from the
    *unclipped* per-state optima ``u_i = b_i / c_i``. Its minimizer on
    ``[0, 1]`` is the projection of the vertex: sum first, then clip,
    ``w_S = clip(sum_i b_i / sum_i c_i, 0, 1)``, with
    ``b_i = E[e_P (e_P - e_C)]`` and ``c_i = E[(e_C - e_P)^2]`` for state
    ``i``. Averaging the already-clipped ``w*_i`` weighted by ``c_i`` would
    give a different, wrong answer (DEF-0003).

    The denominator keeps the ``1e-300`` floor of ``oracle_weight``. It
    cannot bind under P1(a), where ``c >= rho^2 / k``. The function
    ``pooled_floor_count`` counts the pools where it would bind, reported as
    ``pooled_curvature_floor`` in the ``fitting`` block of ``handling``.

    Parameters
    ----------
    moments : EnsembleMoments
        Oracle moments of the states, arrays of shape ``(n, nH)``.
    members : np.ndarray
        State indices of the (state, draw) pairs of the regime, shape
        ``(m,)``. A state appears once per draw that falls in the regime.

    Returns
    -------
    np.ndarray
        Weights, shape ``(nH,)``.

    Raises
    ------
    ValueError
        If ``members`` is empty.
    """
    members = np.asarray(members)
    if members.size == 0:
        raise ValueError("regime_weight needs at least one member")
    return _pooled_weight(moments, members)


def calibrate_regimes(
    tree: DecisionTreeRegressor,
    profile: np.ndarray,
    moments: EnsembleMoments,
    ev: EvaluationDraws,
    theta: float,
    fallback: np.ndarray,
) -> RegimeMap:
    """Compute the weight and median horizon of each regime on calibration.

    The weight of each regime is optimal for it (Theorem P3(a)), and its
    median horizon comes from a Kaplan-Meier estimate (a standard way to
    handle runs that never reach the tolerance, which are "censored").

    Parameters
    ----------
    tree : DecisionTreeRegressor
        Fitted tree.
    profile : np.ndarray
        Calibration profiles, shape ``(n, E, 3)``.
    moments : EnsembleMoments
        Calibration oracle moments (horizons must match ``ev.horizons``).
    ev : EvaluationDraws
        Calibration evaluation draws (used for the realized horizons).
    theta : float
        Tolerance for regime horizons.
    fallback : np.ndarray
        Weights, shape ``(nH,)``, for a regime with no calibration states.

    Returns
    -------
    RegimeMap
        The calibrated regime map. ``empty`` marks the regimes that fell back
        to ``fallback`` (with a NaN Kaplan-Meier horizon), and
        ``pooled_curvature_floor`` counts the floored pools. Neither changes
        a weight.

    Notes
    -----
    The Kaplan-Meier horizon is computed only when the horizons are
    contiguous from 1. This function sees only the core cells, whose horizons
    are ``1..H_max`` (``fit_rules``), so the branch always runs here
    (DEF-0001, WU-0002.11, J: not a silent skip).
    """
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    leaves = tree.apply(profile.reshape(-1, profile.shape[-1])).reshape(
        profile.shape[:2]
    )
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
            err = (
                weights[k] * ev.cp_err[state_idx, draw_idx]
                + (1 - weights[k]) * ev.plp_err[state_idx, draw_idx]
                - ev.verify_noise[state_idx, draw_idx]
            )
            dur, event = realized_horizon(err, ev.horizons, theta)
            horizons_km[k] = kaplan_meier(dur, event, len(ev.horizons)).median()
    return RegimeMap(
        tree=tree,
        leaf_ids=leaf_ids,
        weights=weights,
        horizons_km=horizons_km,
        empty=empty,
        pooled_curvature_floor=pooled_floor,
    )


def regime_regret(
    regime_map: RegimeMap,
    profile: np.ndarray,
    moments: EnsembleMoments,
    column: int,
) -> tuple[float, float]:
    """Return the mean abstraction regret and its ratio to the best single one.

    "Regret" is the extra error caused by using a regime's shared weight
    instead of the state's own best weight.

    Parameters
    ----------
    regime_map : RegimeMap
        Regime map.
    profile : np.ndarray
        Profiles, shape ``(n, E, 3)``.
    moments : EnsembleMoments
        Oracle moments of the same states.
    column : int
        Horizon column.

    Returns
    -------
    tuple[float, float]
        The mean exact excess error ``V(w_k) - V(w*)`` (Theorem P1(a); it
        equals ``c (w_k - w*)^2`` only for states whose ``w*`` is unclipped),
        and its ratio to the mean ``min(E e_C^2, E e_P^2)``. The minimum is
        the definition of the best single forecaster per state, not a guard
        (DEF-0001, J).
    """
    regime = regime_map.assign(profile)
    w_k = regime_map.weights[regime, column]  # (n, E)
    # Only the three second moments enter ``excess_mse``; slice them to one
    # column.
    one_column = replace(
        moments,
        horizons=moments.horizons[column : column + 1],
        sq_cp=moments.sq_cp[:, column : column + 1],
        sq_plp=moments.sq_plp[:, column : column + 1],
        cross=moments.cross[:, column : column + 1],
    )
    regret = float(np.mean(excess_mse(one_column, w_k[:, :, None])))
    best = float(
        np.mean(np.minimum(moments.sq_cp[:, column], moments.sq_plp[:, column]))
    )
    return regret, regret / best
