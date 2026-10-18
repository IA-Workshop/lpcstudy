"""Tests for ``lpcstudy.allocation``: the weights that blend CP and PLP.

The module under test holds the allocation rules (the closed-form weight, the
seed proxy, the regime map and the counters of handled cases). Each test names
an independent reference (a formula written out by hand, a brute-force search
or a manufactured answer) and explains in plain words why its tolerance is
what it is.
"""

from __future__ import annotations

import numpy as np
import pytest

from sklearn.tree import DecisionTreeRegressor

from lpcstudy import allocation
from lpcstudy.allocation import (
    RULE_LABELS,
    RegimeMap,
    SeedProxy,
    closed_form_weight,
    regime_regret,
    regime_weight,
)
from lpcstudy.oracle import curvature, oracle_weight
from unit_helpers import (
    _moments_from_draws,
    moments_from_triples,
    realizable_triples,
)


def test_closed_form_matches_uncorrelated_isotropic_case() -> None:
    """The oracle weight tends to delta^2/(eps^2+delta^2) when independent.

    What is checked: when the CP and PLP errors are independent with variances
    eps^2 and delta^2, the best blend weight tends to
    delta^2/(eps^2+delta^2) (FW Corollary 1).

    Reference: the formula, evaluated by hand as 0.81/0.97 = 0.8351 inside the
    test (not taken from ``closed_form_weight``). The quantity tested is
    ``oracle_weight`` applied to plain sample moments of 200 000 independent
    draws (the moments come from a test helper, not from
    ``lpcstudy.ensemble``).

    Tolerance ``abs=5e-3``: this is Monte Carlo (random sampling) error, kept
    unchanged. The delta-method standard error of the sample weight
    w = (b - c)/(a + b - 2c), with a, b the sample second moments and c the
    sample cross moment, at N = 200 000 is
    sqrt([(b/D^2)^2 2 a^2 + (a/D^2)^2 2 b^2 + ((b-a)/D^2)^2 a b]/N) = 8.3e-4
    (a = eps^2, b = delta^2, D = a + b), so 5e-3 is 6.0 standard errors.
    """
    rng = np.random.default_rng(2)
    eps, delta = 0.4, 0.9
    cp = eps * rng.standard_normal((1, 200_000, 1))
    plp = delta * rng.standard_normal((1, 200_000, 1))
    w_star = oracle_weight(_moments_from_draws(cp, plp))[0, 0]
    analytic = delta**2 / (eps**2 + delta**2)
    assert w_star == pytest.approx(analytic, abs=5e-3)


def test_closed_form_weight_exact_values() -> None:
    """``closed_form_weight`` equals delta^2/(eps^2+delta^2) on easy cases.

    Reference: the formula evaluated on exact fractions (FW Corollary 1).
    The pair 0.16, 0.81 gives 81/97. Setting eps^2 = 0 gives 1, and
    delta^2 = 0 gives 0 (the weight sits entirely on the more accurate
    forecaster). Equal seeds give 1/2.

    Tolerance ``rel=1e-14``: the function does one addition and one division
    in float64, so the relative error is at most about 3 * 1.1e-16 = 3.3e-16.
    A bound of 1e-14 leaves a factor of 30 of room.
    """
    got = closed_form_weight(
        np.array([0.16, 0.0, 0.5, 0.3]), np.array([0.81, 2.0, 0.0, 0.3])
    )
    assert got == pytest.approx([81 / 97, 1.0, 0.0, 0.5], rel=1e-14, abs=0.0)


def test_seed_proxy_recovers_parameters() -> None:
    """The seed-proxy fit recovers slope and floor of seed^2 = a f^2 + b g^2.

    What is checked: least squares on the log scale returns the coefficients
    (a, b) that generated the data.

    Reference: a manufactured answer. The data are generated with the known
    (a, b) = (2, 3) and multiplicative log-normal noise of standard deviation
    0.01, with n = 500 states.

    Tolerances ``rel=0.02`` (slope) and ``rel=0.05`` (floor), kept unchanged.
    The linearized standard errors of log a and log b are the square roots of
    the diagonal of sigma^2 (J^T J)^-1, with J the Jacobian of log(seed^2) with
    respect to (log a, log b) on the test's own 500 states and sigma = 0.01:
    5.8e-4 and 1.7e-3 (relative errors of a and b). The tolerances are
    therefore about 34 and 29 standard errors. That is loose on purpose, to
    leave room for the soft-L1 loss (for residuals near 0.01 it differs from a
    quadratic by a relative z/4 = 2.5e-5, with z the squared residual) and for
    the nonlinearity.
    """
    rng = np.random.default_rng(5)
    rho = 0.02
    feature = rng.uniform(0.01, 0.2, 500)
    floor = rho * rng.uniform(0.5, 2.0, 500)
    seed_sq = (2.0 * feature**2 + 3.0 * floor**2) * np.exp(
        0.01 * rng.standard_normal(500)
    )
    proxy = SeedProxy.fit(feature**2, floor**2, seed_sq)
    assert proxy.slope == pytest.approx(2.0, rel=0.02)
    assert proxy.floor == pytest.approx(3.0, rel=0.05)


def test_rule_set_is_the_v3_rule_set() -> None:
    """The rule labels are exactly A0-A5, A4o and A*; A4f is gone (WU-0002.1).

    Reference: proposal and methods v3 section 5 (rules A0 to A5, A4o, A*) and
    the decision log (rule A4f was dropped), written out in the test and not
    read from the code. Tolerance: none, because this is an equality of two
    sets of strings.
    """
    assert set(RULE_LABELS) == {
        "A0",
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A4o",
        "A*",
    }
    assert not hasattr(allocation, "full_form_weight")


def test_regime_regret_is_mean_exact_excess() -> None:
    """``regime_regret`` is the mean over (state, draw) of V(w_k) - V(w*).

    What is checked: the regret is the exact excess error, not the shortcut
    c (w_k - w*)^2 (which is wrong when the best weight w* is clipped to the
    interval [0, 1]).

    Reference: brute force. For each state the excess is V(w_k) minus the
    minimum of V over ``np.linspace(0, 1, 10_000)``, with V evaluated directly
    from the moment triple (the grid argument of
    ``test_excess_mse_matches_grid_minimum``). The reference is the mean of
    these over the states (each state appears E = 2 times with the same
    regime).

    Setup: a 2-leaf tree on a 1-D synthetic profile (140 states, 2 horizon
    columns; the regret is requested at column 1). Leaf 0 holds 70 states with
    u in (1, 6) or [0.6, 1] and w_k = 0.35. Leaf 1 holds 70 states with u in
    (-5, 0) or [0, 0.2] and w_k = 0.7. So |w_k - w*| >= 0.25 >= 0.1 for every
    state, which the test asserts as a precondition on the weights the code
    returns. Half of the states have u outside [0, 1]. The second output is
    checked against the mean of min(E_C, E_P), written out here.

    Tolerance ``rtol=1e-6``: the grid minimum exceeds V(w*) by at most
    c (h/2)^2 = 2.5e-9 c with h = 1/9999, and the excess is at least
    c (w_k - w*)^2 >= 0.0625 c, so the relative bias is at most 4e-8 (the
    argument of the 10-fold looser bound at 0.1). Round-off is about 1e-12.
    The test also asserts that the old shortcut c (w - w*)^2 mean is below the
    exact value by more than 1e-3 relative, so it would detect DEF-0002 (the
    old wrong formula) coming back.
    """
    rng = np.random.default_rng(31)
    parts = []
    for _ in range(2):  # two horizon columns, each with its own triples
        left = realizable_triples(rng, 0, 20, 50, inside=(0.6, 1.0))
        right = realizable_triples(rng, 50, 20, 0, inside=(0.0, 0.2))
        parts.append({k: np.concatenate([left[k], right[k]]) for k in left})
    n_states = 140
    e_c = np.stack([p["E_C"] for p in parts], axis=1)
    e_p = np.stack([p["E_P"] for p in parts], axis=1)
    cross = np.stack([p["C"] for p in parts], axis=1)
    moments = moments_from_triples(e_c, e_p, cross)
    x = np.concatenate(
        [-rng.uniform(0.5, 1.5, (70, 2)), rng.uniform(0.5, 1.5, (70, 2))]
    )
    profile = x[:, :, None]  # (140, 2, 1)
    label = (x[:, 0] > 0).astype(float)
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0)
    tree.fit(profile.reshape(-1, 1), np.repeat(label, 2))
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    regime_map = RegimeMap(
        tree=tree,
        leaf_ids=leaf_ids,
        weights=np.array([[0.4, 0.35], [0.6, 0.7]]),
        horizons_km=np.full(2, np.nan),
    )
    column = 1
    regime = regime_map.assign(profile)
    assert np.array_equal(
        regime[:, 0], np.r_[np.zeros(70, int), np.ones(70, int)]
    )
    w_k = regime_map.weights[regime, column]
    w_star = oracle_weight(moments)[:, column]
    assert np.all(
        np.abs(w_k - w_star[:, None]) >= 0.1
    )  # precondition of the grid reference
    unclipped = oracle_weight(moments, clip=False)[:, column]
    assert np.mean((unclipped < 0) | (unclipped > 1)) >= 0.4

    grid = np.linspace(0.0, 1.0, 10_000)

    def direct_v(weight: np.ndarray) -> np.ndarray:
        return (
            weight**2 * e_c[:, [column]]
            + (1 - weight) ** 2 * e_p[:, [column]]
            + 2 * weight * (1 - weight) * cross[:, [column]]
        )

    v_min = direct_v(grid[None, :]).min(axis=1)
    reference = float(np.mean(direct_v(w_k) - v_min[:, None]))
    regret, ratio = regime_regret(regime_map, profile, moments, column)
    assert regret == pytest.approx(reference, rel=1e-6, abs=0.0)
    best = float(np.mean(np.minimum(e_c[:, column], e_p[:, column])))
    assert ratio == pytest.approx(regret / best, rel=1e-12, abs=0.0)
    old = float(
        np.mean(curvature(moments)[:, [column]] * (w_k - w_star[:, None]) ** 2)
    )
    assert old < reference * (1.0 - 1e-3)


def test_regime_weight_matches_brute_force() -> None:
    """``regime_weight`` is clip(sum b / sum c), the best common weight (P3(a)).

    What is checked: the closed form returns the same weight as a brute-force
    search for the minimizer of sum_i V_i(w) over the members of a regime.

    Reference: brute force on the direct quadratic
    V_i(w) = w^2 E_C + (1-w)^2 E_P + 2w(1-w) C, summed over the members (with
    multiplicity). Stage 1 is the argmin g over ``np.linspace(0, 1, 10_000)``.
    Stage 2 is the argmin g2 over 10_000 points of [g - h, g + h] cap [0, 1]
    (h = 1/9999, spacing about 2e-8). Stage 2 is needed because a single grid
    quantizes the argmin to h/2 = 5e-5, which is above the tolerance (this
    strengthens the reference and does not change the tolerance).

    Setup: 50 regimes of 5 to 40 members from the manufactured generator.
    Ten have all u > 1, ten have all u < 0, ten mix u < 0 and u > 1 (none in
    [0, 1]), and 20 draw u over all three strata. In 10 regimes some member
    indices repeat 2 to 4 times (one state counted once per draw that falls in
    the regime), and the brute-force sum is weighted the same way.

    Tolerance ``abs=1e-6``: |g2 - w_S| <= h2/2 + sqrt(delta / S_c) with
    h2 = 2e-8 and the round-off of the sum delta <= 9 eps * 138 S_c
    (V <= 46 c per member). That is about 1e-8 + 3.7e-7 = 3.8e-7, a margin of
    2.6. The mathematician's measurement on 200 such regimes gave 3.9e-8.

    Sensitivity: in at least one mixed regime the old curvature-weighted mean
    of the clipped w* misses the reference by more than 1e-2 (DEF-0003), so the
    test would catch that old formula.
    """
    rng = np.random.default_rng(4242)
    grid = np.linspace(0.0, 1.0, 10_000)
    spacing = 1.0 / 9999.0
    n_repeated = n_old_misses = 0
    for index in range(50):
        size = int(rng.integers(5, 41))
        if index < 10:
            counts = (0, 0, size)
        elif index < 20:
            counts = (size, 0, 0)
        elif index < 30:
            below = int(rng.integers(1, size))
            counts = (below, 0, size - below)
        else:
            counts = tuple(
                int(x) for x in rng.multinomial(size, [1 / 3, 1 / 3, 1 / 3])
            )
        t = realizable_triples(rng, *counts)
        moments = moments_from_triples(
            t["E_C"][:, None], t["E_P"][:, None], t["C"][:, None]
        )
        members = np.arange(size)
        if index % 5 == 0:
            extra = rng.choice(
                size, size=int(rng.integers(1, size + 1)), replace=False
            )
            members = np.concatenate(
                [members] + [extra] * int(rng.integers(1, 4))
            )
            n_repeated += 1
        got = regime_weight(moments, members)
        assert got.shape == (1,)

        def total(weights: np.ndarray) -> np.ndarray:
            v = (
                weights[None, :] ** 2 * t["E_C"][:, None]
                + (1 - weights[None, :]) ** 2 * t["E_P"][:, None]
                + 2
                * weights[None, :]
                * (1 - weights[None, :])
                * t["C"][:, None]
            )
            return v[members].sum(axis=0)

        g = grid[np.argmin(total(grid))]
        fine = np.linspace(max(g - spacing, 0.0), min(g + spacing, 1.0), 10_000)
        g2 = fine[np.argmin(total(fine))]
        assert abs(got[0] - g2) <= 1e-6, (index, got[0], g2)
        if 20 <= index < 30:
            old_w = oracle_weight(moments)[members, 0]
            old_c = curvature(moments)[members, 0]
            old = float(np.sum(old_c * old_w) / np.sum(old_c))
            n_old_misses += abs(old - g2) > 1e-2
    assert n_repeated >= 5
    assert n_old_misses >= 1


def test_regime_weight_rejects_empty_members() -> None:
    """An empty regime raises ``ValueError`` (no silent fallback; PRIME.4).

    Reference: the documented contract of the function. Tolerance: none,
    because only the type of the exception is checked.
    """
    moments = moments_from_triples(
        np.ones((3, 1)), np.ones((3, 1)), np.zeros((3, 1))
    )
    with pytest.raises(ValueError, match="at least one member"):
        regime_weight(moments, np.array([], dtype=int))


# ------------------------------------------- WU-0002.11a: counters (DEF-0001)
def test_floor_counters_a5_count_and_leave_outputs_unchanged() -> None:
    """A5: the floor counters count where a floor binds and change no output.

    What is checked: ``closed_form_floor_count`` and ``pooled_floor_count``
    count the entries where the ``1e-300`` floor of a denominator binds, and
    the weights are unchanged by the counting.

    Reference: hand-built inputs, with the expected counts read off the
    construction.

    (a) Squared seeds ``eps^2 = [0.16, 0, 0.5, nan]`` and
    ``delta^2 = [0.81, 0, 0.0, 0.3]``: only the second pair has a sum below
    1e-300 (the NaN pair is not counted, because ``NaN < x`` is False), so the
    count is 1.

    (b) Moments of 4 states by 3 horizons with ``E_C = E_P = C = 1`` at
    (state 0, horizon 0) and 2 elsewhere (``c = E_C + E_P - 2C``, which is 0
    at that one entry and 2 elsewhere). The pool of all states has
    ``sum c = 6`` at horizon 0, so no floor binds (count 0). The members [0]
    alone have ``sum c = 0`` at horizon 0 (count 1), and members [1, 2] count 0.

    The outputs of ``closed_form_weight``, ``global_weight`` and
    ``regime_weight`` equal the expressions as they were written before the
    counters existed, bit for bit. This is a regression guard (it compares the
    code with its earlier form, so it is not correctness evidence by itself),
    and it also confirms that sharing a helper between ``global_weight`` and
    ``regime_weight`` changed nothing.
    """
    from lpcstudy.allocation import (
        closed_form_floor_count,
        global_weight,
        pooled_floor_count,
    )

    eps_sq = np.array([0.16, 0.0, 0.5, np.nan])
    delta_sq = np.array([0.81, 0.0, 0.0, 0.3])
    assert closed_form_floor_count(eps_sq, delta_sq) == 1
    old_cf = delta_sq / np.maximum(eps_sq + delta_sq, 1e-300)
    assert closed_form_weight(eps_sq, delta_sq).tobytes() == old_cf.tobytes()

    e_c = np.full((4, 3), 2.0)
    e_p = np.full((4, 3), 2.0)
    cross = np.full((4, 3), 1.0)  # c = 2 + 2 - 2 = 2
    e_c[0, 0], e_p[0, 0], cross[0, 0] = 1.0, 1.0, 1.0  # c = 0
    moments = moments_from_triples(e_c, e_p, cross)
    assert float(curvature(moments)[0, 0]) == 0.0
    assert pooled_floor_count(moments) == 0
    assert pooled_floor_count(moments, np.array([0])) == 1
    assert pooled_floor_count(moments, np.array([1, 2])) == 0
    old_a2 = np.clip(
        np.sum(moments.sq_plp - moments.cross, axis=0)
        / np.maximum(np.sum(curvature(moments), axis=0), 1e-300),
        0.0,
        1.0,
    )
    assert global_weight(moments).tobytes() == old_a2.tobytes()
    members = np.array([0, 3, 3])
    old_rw = np.clip(
        np.sum((moments.sq_plp - moments.cross)[members], axis=0)
        / np.maximum(np.sum(curvature(moments)[members], axis=0), 1e-300),
        0.0,
        1.0,
    )
    assert regime_weight(moments, members).tobytes() == old_rw.tobytes()


def test_nu_cap_and_constant_target_counters_a9() -> None:
    """A9: the cap counter and the constant-target counter count correctly.

    What is checked: ``nu_cap_clip_count`` counts only entries strictly above
    the cap, and ``constant_target_count`` counts each constant tree target
    once.

    Reference: hand arrays. With nu_hat = [1, 2, 10, 11, 12, 13, 5, 10] and
    cap 10, three values are above the cap (11, 12, 13), and two equal the cap
    (``np.minimum`` does not change them, so they are not counted): the count
    is 3. The values changed by ``ProfileProxies.features`` are exactly those,
    checked on the same array.

    Constant targets: w constant 0.5 with a varying log-horizon gives 1; both
    constant gives 2; neither gives 0. A target constant up to round-off
    (0.1 repeated, standard deviation of order 1e-17 < 1e-12) is counted. A
    target with spread 1e-6 (above the 1e-12 guard) is not counted. All
    results are exact integers, so there is no tolerance.
    """
    from lpcstudy.allocation import (
        ProfileProxies,
        constant_target_count,
        nu_cap_clip_count,
    )

    nu = np.array([1.0, 2.0, 10.0, 11.0, 12.0, 13.0, 5.0, 10.0])
    assert nu_cap_clip_count(nu, 10.0) == 3
    capped = ProfileProxies.features(np.ones(8), nu, 0.01, 10.0)["est_f"] / 0.01
    assert int(np.sum(capped != nu)) == 3
    varying = np.linspace(0.0, 1.0, 20)
    assert constant_target_count(np.full(20, 0.5), varying) == 1
    assert constant_target_count(np.full(20, 0.5), np.full(20, 2.0)) == 2
    assert constant_target_count(varying, varying + 1.0) == 0
    assert constant_target_count(np.full(20, 0.1), varying) == 1
    assert constant_target_count(1e-6 * varying, varying) == 0


def test_calibrate_regimes_counts_an_empty_regime_a6() -> None:
    """A6: a tree leaf that no calibration profile reaches is flagged.

    What is checked: an empty regime is flagged in ``empty``, takes the
    fallback weights exactly (bit for bit), and has a NaN Kaplan-Meier horizon.

    Reference: a hand construction. A 2-leaf tree is fitted on a 1-D profile
    with x = -1 (target 0) and x = +1 (target 1), so the leaves are the two
    half-lines. The calibration profiles are all x = +1, so the leaf of x = -1
    is never reached and exactly one regime is empty. There are 20 calibration
    states with 2 draws each and horizons 1..4 (contiguous, so the
    Kaplan-Meier step runs for the reached regime). The CP and PLP errors are
    1.0 everywhere and the verification noise is 0, so every realized error is
    1.0 > theta = 0.2 at horizon 1, and the reached regime has Kaplan-Meier
    median 1 (finite). The ``fallback`` is the vector [0.1, 0.3, 0.7, 0.9],
    whose entries cannot be written exactly in binary floating point, and the
    empty row must equal it bit for bit.

    Expected: ``empty`` has exactly one True (the x = -1 leaf), ``horizons_km``
    is NaN there and finite elsewhere, and ``pooled_curvature_floor == 0``
    (because c = 2 > 0).
    """
    from lpcstudy.allocation import calibrate_regimes
    from lpcstudy.ensemble import EvaluationDraws

    x_fit = np.concatenate([-np.ones(10), np.ones(10)])
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0)
    tree.fit(x_fit.reshape(-1, 1), (x_fit > 0).astype(float))
    left_leaf = int(tree.apply(np.array([[-1.0]]))[0])
    n_states, n_draws, n_hor = 20, 2, 4
    profile = np.ones((n_states, n_draws, 1))
    moments = moments_from_triples(
        np.full((n_states, n_hor), 2.0),
        np.full((n_states, n_hor), 2.0),
        np.full((n_states, n_hor), 1.0),
    )
    ones = np.ones((n_states, n_draws, n_hor))
    evals = EvaluationDraws(
        horizons=np.arange(1, n_hor + 1),
        cp_err=ones,
        plp_err=ones,
        verify_noise=np.zeros_like(ones),
        distance=np.zeros((n_states, n_draws)),
        est_nu=np.zeros((n_states, n_draws)),
        growth_proxy=np.zeros((n_states, n_draws)),
        gain_proxy=ones,
        inputs=np.zeros((n_states, n_draws, 1)),
        noise_sens=np.zeros((n_states, n_draws)),
    )
    fallback = np.array([0.1, 0.3, 0.7, 0.9])
    result = calibrate_regimes(tree, profile, moments, evals, 0.2, fallback)
    left = int(np.nonzero(result.leaf_ids == left_leaf)[0][0])
    assert int(result.empty.sum()) == 1 and bool(result.empty[left])
    assert result.weights[left].tobytes() == fallback.tobytes()
    assert np.isnan(result.horizons_km[left])
    assert np.all(np.isfinite(result.horizons_km[~result.empty]))
    assert result.pooled_curvature_floor == 0


# ------------------------------ WU-0003.7a: nfev, status, A5 leaf digest
def test_seed_proxy_records_nfev_and_status_equal_to_scipys_optimize_result() -> (
    None
):
    """``SeedProxy.fit`` stores ``nfev`` and ``status`` of its scipy call (a3).

    What is checked: the number of function evaluations (``nfev``) and the
    termination status that the proxy records are the ones scipy reports.

    Reference: scipy's own ``OptimizeResult`` for the same problem, run inside
    the test. It uses the same manufactured data, the non-negative
    least-squares start ``nnls`` and the log-scale soft-L1 residual written
    out here from the docstring of ``SeedProxy``. The data have the known
    solution (a, b) = (2, 3) (the generator, seed and tolerances of the
    recovery test above: rel 0.02 and 0.05, which are 34 and 29 standard
    errors), once with multiplicative log-normal noise of standard deviation
    0.01 and once exact (no noise).

    ``nfev`` and ``status`` are integers, so they are compared exactly. The
    same inputs run the same deterministic code in one process, so equality is
    the expectation. Preconditions are asserted so that the test cannot pass
    on a constant: the noisy fit needs more than one evaluation and stops by a
    tolerance (status 1 to 4). A hand-built proxy has ``None`` for both
    (it was not fitted), and ``vars`` gives the four JSON leaves in the order
    slope, floor, nfev, status.
    """
    import json

    from scipy.optimize import least_squares, nnls

    def scipy_fit(
        feature_sq: np.ndarray, floor_sq: np.ndarray, seed_sq: np.ndarray
    ):
        scale = np.median(seed_sq)
        design = np.column_stack([feature_sq, floor_sq]) / scale
        coef, _ = nnls(design, seed_sq / scale)
        log_seed = np.log(seed_sq / scale)
        return least_squares(
            lambda x: np.log(design @ np.exp(x) + 1e-300) - log_seed,
            np.log(np.maximum(coef, 1e-6)),
            loss="soft_l1",
        )

    rng = np.random.default_rng(5)
    rho = 0.02
    feature = rng.uniform(0.01, 0.2, 500)
    floor = rho * rng.uniform(0.5, 2.0, 500)
    exact = 2.0 * feature**2 + 3.0 * floor**2
    noisy = exact * np.exp(0.01 * rng.standard_normal(500))
    for seed_sq, is_noisy in ((noisy, True), (exact, False)):
        proxy = SeedProxy.fit(feature**2, floor**2, seed_sq)
        sol = scipy_fit(feature**2, floor**2, seed_sq)
        assert type(proxy.nfev) is int and type(proxy.status) is int
        assert (proxy.nfev, proxy.status) == (sol.nfev, sol.status)
        assert proxy.slope == pytest.approx(2.0, rel=0.02)
        assert proxy.floor == pytest.approx(3.0, rel=0.05)
        if is_noisy:
            assert sol.nfev > 1 and sol.status in (1, 2, 3, 4)
    hand = SeedProxy(0.5, 0.25)
    assert (hand.nfev, hand.status) == (None, None)
    leaves = vars(SeedProxy(0.5, 0.25, nfev=7, status=2))
    assert list(leaves) == ["slope", "floor", "nfev", "status"]
    assert json.loads(json.dumps(leaves)) == leaves


def _stump() -> tuple[DecisionTreeRegressor, RegimeMap]:
    """Build a 2-leaf tree on one profile coordinate, split at exactly 0.5.

    The tree is fitted on the two points 0.0 and 1.0 with different labels,
    so the split is their midpoint. By hand, a value <= 0.5 goes to node 1 and
    a value > 0.5 to node 2 (scikit-learn numbers the root 0, then its left
    child 1 and its right child 2).
    """
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0)
    tree.fit(np.array([[0.0], [1.0]]), np.array([0.0, 1.0]))
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    assert leaf_ids.tolist() == [1, 2] and tree.tree_.threshold[0] == 0.5
    return tree, RegimeMap(
        tree=tree,
        leaf_ids=leaf_ids,
        weights=np.zeros((2, 1)),
        horizons_km=np.full(2, np.nan),
    )


def test_regime_leaf_digest_equals_sha256_of_the_int64_leaf_index_and_tracks_one_leaf() -> (
    None
):
    """``RegimeMap.leaf_digest`` is the SHA-256 of the int64 leaf ids (a4).

    What is checked: the fingerprint is the SHA-256 hash of the leaf id of
    every (state, draw), and it changes when one state moves to another leaf.

    Reference: the leaf of every (state, draw) is decided by hand from the
    manufactured split at 0.5 (a value <= 0.5 is node 1, above is node 2). The
    leaves are packed as little-endian int64 with ``struct`` and hashed with
    ``hashlib``, the first profile array first and the second after it, each
    flattened in C order. All of this is written in the test and does not go
    through ``index_digest``. The profiles have shape ``(n, E, 1)``.

    Checks: the digest equals the hand value. Moving one state's coordinate
    across the split (0.4 to 0.8) changes the digest to the new hand value.
    Moving it within its leaf (0.1 to 0.3) leaves the digest unchanged. The
    order of the two arrays matters. ``tree.apply`` equals the hand leaves (the
    reference there is the tree's own definition). Everything is exact, so
    there is no tolerance.
    """
    import hashlib
    import struct

    tree, regime_map = _stump()
    # Calibration has n = 3 states and E = 2 draws; test has n = 2 and E = 2.
    calibration = np.array([[0.1, 0.9], [0.4, 0.6], [0.0, 1.0]])[..., None]
    test = np.array([[0.7, 0.2], [0.5, 0.51]])[..., None]

    def by_hand(*profiles: np.ndarray) -> str:
        leaves = [
            1 if x <= 0.5 else 2 for p in profiles for x in p[..., 0].ravel()
        ]
        return hashlib.sha256(
            struct.pack("<%dq" % len(leaves), *leaves)
        ).hexdigest()

    assert regime_map.leaf_digest(calibration, test) == by_hand(
        calibration, test
    )
    flipped = calibration.copy()
    flipped[1, 0, 0] = 0.8  # was 0.4: node 1 becomes node 2
    assert regime_map.leaf_digest(flipped, test) == by_hand(flipped, test)
    assert regime_map.leaf_digest(flipped, test) != regime_map.leaf_digest(
        calibration, test
    )
    inside = calibration.copy()
    inside[0, 0, 0] = 0.3  # was 0.1: the same leaf
    assert regime_map.leaf_digest(inside, test) == regime_map.leaf_digest(
        calibration, test
    )
    assert regime_map.leaf_digest(test, calibration) != regime_map.leaf_digest(
        calibration, test
    )
    assert tree.apply(calibration.reshape(-1, 1)).tolist() == [
        1 if x <= 0.5 else 2 for x in calibration.ravel()
    ]
