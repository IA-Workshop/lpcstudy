"""Tests of the multi-start state estimator (WU-0039, fixes F1 and F2).

The V7 diagnosis (note ``docs/agent/notes/2026-10-25-v7-diagnosis.md``,
sections 5 and 6) found that on S2, S4, S5 and S6 the Levenberg-Marquardt
(LM) refinement from the network start often ends in a wrong local minimum.
Fix F1 refines from a second start, the nearest of the estimator's own
training pairs, and keeps the lower final cost; F2 adds a window-continuation
start. The switch is ``SystemSpec.estimator_starts``.

What is checked, with the independent reference of each check:

* The two-start LM reaches the global minimum of a manufactured cost with two
  basins. Reference: a grid scan of the cost (no LM), and the manufactured
  truth.
* Ties go to the network start, and the selection counts equal the counts
  known by construction.
* With the switch off, the multi-start code is never entered (the single-start
  function is bitwise the one ``test_estimation.py::test_l4`` pins).
* The pair search equals a brute-force argmin of the distances.
* The continuation stages ignore the newest delay coordinate (bitwise), and
  are the identity when ``D <= m + 1``.
* Non-finite events of every start are counted; bad input raises.
* The tallies reach the ``handling`` block only for a multi-start system.

The toy world is built by hand: a two-component map, ``D = 7``, delay 1,
identity whitening, mean 0, and a stub network returning the chosen start.
Data come from literal ``np.random.default_rng(<int>)`` (development, not a
study seed).
"""

from __future__ import annotations

import functools
from types import SimpleNamespace

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy.config import StudyConfig
from lpcstudy.dynamics import delay_map_forward
from lpcstudy.estimation import START_DECREASE, StateEstimator
from lpcstudy.pipeline import Study
from lpcstudy.systems import (
    F1_STARTS,
    F2_STARTS,
    SINGLE_START,
    SYSTEMS,
    SystemSpec,
    check_starts,
    lorenz63_field,
)

EMBED = 7
TAU = 1
DECAY = 0.9
TRUTH = np.array([0.3, 1.0])
NOISE = 0.01
GRID_STEP = 1e-4


def toy_step(state: jnp.ndarray) -> jnp.ndarray:
    """The toy map ``(x, y) -> (y^2 + y/2, 0.9 y)``.

    The observed ``x`` after ``n >= 1`` steps is ``a_n y^2 + b_n y`` with
    ``a_n = 0.81^(n-1)`` and ``b_n = 0.5 * 0.9^(n-1)``. The ratio ``b_n / a_n``
    changes with ``n``, so a negative ``y`` can fit the window only
    approximately: the cost has a global minimum near the truth ``y = 1`` and
    a second, local minimum near ``y = -1.58`` (cost about 0.17; found by the
    grid scan below, not assumed).
    """
    x, y = state[0], state[1]
    return jnp.stack([y**2 + 0.5 * y, DECAY * y])


class _StubNetwork:
    """A network whose ``predict`` returns the start ``u0`` the test sets."""

    width = 0

    def __init__(self, u0: np.ndarray) -> None:
        self.u0 = u0

    def predict(self, inputs):
        return jnp.asarray(self.u0)


@functools.lru_cache(maxsize=None)
def _toy():
    """Return the delay map, the pair states and the toy context.

    The pairs are a near-truth state and two decoys in other regions, with
    their noise-free delay vectors (``delay_map_forward``, the same map as
    the estimator).
    """
    fwd = jax.jit(delay_map_forward(toy_step, 0, 0.0, 1.0, TAU, EMBED))
    pair_states = np.array([[0.3, 0.95], [0.0, -2.5], [1.0, 2.0]])
    pair_inputs = np.asarray(jax.vmap(fwd)(jnp.asarray(pair_states)))
    ctx = SimpleNamespace(
        unwhiten=np.eye(2),
        whiten=np.eye(2),
        state_mean=np.zeros(2),
        spec=SimpleNamespace(observed_index=0),
        obs_mean=0.0,
        obs_scale=1.0,
        delay=TAU,
        embed_dim=EMBED,
        history=(EMBED - 1) * TAU,
        estimator_inputs=pair_inputs,
        estimator_targets=pair_states,
    )
    return fwd, pair_states, pair_inputs, ctx


def _noisy_targets(n: int, seed: int) -> np.ndarray:
    """Return ``n`` noisy delay vectors of the truth (noise ``0.01``)."""
    fwd = _toy()[0]
    clean = np.asarray(fwd(jnp.asarray(TRUTH)))
    rng = np.random.default_rng(seed)
    return clean[None, :] + NOISE * rng.standard_normal((n, EMBED))


def _grid_minima(target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return the local minima ``(y, cost)`` of the cost on a grid in ``y``.

    ``x`` enters only the oldest coordinate, ``X[D-1] = x``, so the optimal
    ``x`` is ``target[D-1]`` exactly, and the cost is a function of ``y``
    alone. The grid is ``[-4, 4]`` in steps of ``GRID_STEP``. This is the
    independent reference: no LM is involved.
    """
    fwd = _toy()[0]
    ys = np.linspace(-4.0, 4.0, 80_001)
    states = np.stack([np.full_like(ys, target[-1]), ys], axis=1)
    model = np.asarray(jax.vmap(fwd)(jnp.asarray(states)))
    cost = np.sum((target[None, :] - model) ** 2, axis=1)
    inner = (cost[1:-1] < cost[:-2]) & (cost[1:-1] < cost[2:])
    index = np.where(inner)[0] + 1
    return ys[index], cost[index]


def _estimator(u0: np.ndarray, starts: tuple[str, ...]) -> StateEstimator:
    """Return a toy estimator with the stub network start ``u0``."""
    ctx = _toy()[3]
    return StateEstimator(
        ctx=ctx,
        network=_StubNetwork(u0),
        model_step=toy_step,
        refine_steps=15,
        starts=starts,
    )


# Network starts: rows 0-2 in the wrong basin, rows 3-5 in the right one.
WRONG = (-1.7, -2.0, -1.4)
RIGHT = (0.9, 1.05, 1.2)


def _starts() -> np.ndarray:
    return np.array([[0.3, y] for y in (*WRONG, *RIGHT)])


def test_two_start_lm_reaches_the_global_minimum_of_a_two_basin_cost() -> None:
    """F1 keeps the global minimum where the network start finds a local one.

    Reference: per row, the grid scan of the cost in ``y`` (no LM), which
    shows two local minima, the global one near the truth ``y = 1``.
    Tolerance: the LM cost is at most the grid minimum plus ``1e-12`` (LM
    converges below the grid) and at least the grid minimum minus ``1e-7``
    (on a grid of step ``h = 1e-4`` the grid minimum exceeds the true one by
    at most ``c'' (h / 2)^2 / 2``, about ``4e-8`` with ``c'' <= 30``); the
    LM ``y`` is within ``h`` of the grid minimizer (``h / 2`` of grid
    resolution plus convergence error far below it). ``y`` is read off the
    end-of-window state, ``s_t[1] = 0.9^6 y`` (six multiplications, error
    about ``1e-15``).
    """
    targets = _noisy_targets(6, seed=3901)
    u0 = _starts()
    single = _estimator(u0, SINGLE_START)
    two = _estimator(u0, F1_STARTS)
    _, _, _, _, lm_single = single.estimate_counted(targets)
    states, _, _, _, lm_two = two.estimate_counted(targets)
    y_two = states[:, 1] / DECAY ** (EMBED - 1)
    for row, target in enumerate(targets):
        ys, costs = _grid_minima(target)
        assert len(ys) == 2, (row, ys)  # two basins, as constructed
        best = int(np.argmin(costs))
        assert abs(ys[best] - 1.0) < 0.05 and ys[1 - best] < -1.0
        assert costs[1 - best] > costs[best] + 0.1
        c_two = lm_two.residual[row]
        assert costs[best] - 1e-7 <= c_two <= costs[best] + 1e-12, row
        assert abs(y_two[row] - ys[best]) <= GRID_STEP, row
        if row < len(WRONG):
            # Precondition: the single network start ends in the local one.
            assert lm_single.residual[row] > costs[best] + 0.1, row
    assert lm_single.start_selected is None
    picked = lm_two.start_selected
    assert picked[: len(WRONG)].tolist() == [1, 1, 1]
    assert lm_two.start_material[: len(WRONG)].all()
    # Rows 3-5: both starts reach the same minimum; any switch is round-off,
    # never material (the costs are about 4e-4, far above round-off).
    assert not lm_two.start_material[len(WRONG) :].any()


def test_start_counts_equal_the_counts_known_by_construction() -> None:
    """The tally counts estimates, switches and material switches exactly.

    Reference: the selections of the rows, known from the construction of
    the previous test (three material switches in six rows) and recounted
    from the per-estimate arrays; two calls add up. Tolerance: none.
    """
    targets = _noisy_targets(6, seed=3901)
    two = _estimator(_starts(), F1_STARTS)
    lm = two.estimate_counted(targets)[4]
    two.estimate_counted(targets)
    switched = int(np.sum(lm.start_selected != 0))
    record = two.start_record()
    assert record == {
        "starts": ["network", "pair"],
        "estimates": 12,
        "selected": {"network": 2 * (6 - switched), "pair": 2 * switched},
        "lm_start_switched": 2 * switched,
        "lm_start_switched_material": 6,
    }
    assert switched >= 3
    assert all(type(v) is int for v in record["selected"].values())


def test_material_switch_needs_a_relative_decrease_above_the_threshold() -> (
    None
):
    """``start_material`` follows ``c_net - c_sel > 1e-6 c_net`` on each row.

    Reference: the final costs of the network-only estimator (the default
    function, not the code under test) and of the selected run, compared by
    the definition in NumPy. Rows where the two differ by less than ``1e-3``
    relative are left out: there the network run of the multi-start function
    and of the single-start function may differ by round-off. Tolerance: none
    on the flag.
    """
    targets = _noisy_targets(6, seed=3902)
    u0 = _starts()
    c_net = _estimator(u0, SINGLE_START).estimate_counted(targets)[4].residual
    lm = _estimator(u0, F1_STARTS).estimate_counted(targets)[4]
    clear = np.abs(c_net - lm.residual) > 1e-3 * c_net
    expected = (lm.start_selected != 0) & (
        c_net - lm.residual > START_DECREASE * c_net
    )
    assert clear[: len(WRONG)].all()
    assert (lm.start_material[clear] == expected[clear]).all()


def test_ties_go_to_the_network_start() -> None:
    """When the pair start equals the network start, the network is kept.

    Reference: construction. The only pair is the network start itself (its
    delay vector is the query's nearest training input), so the two runs are
    the same arithmetic on the same numbers and their costs are equal; the
    rule keeps the strictly lower cost and gives ties to the network.
    Tolerance: none.
    """
    fwd, _, _, ctx = _toy()
    u0 = np.array([[0.3, -1.7], [0.3, 1.1]])
    tie_ctx = SimpleNamespace(
        **{
            **vars(ctx),
            "estimator_inputs": np.asarray(jax.vmap(fwd)(jnp.asarray(u0))),
            "estimator_targets": u0,
        }
    )
    est = StateEstimator(
        ctx=tie_ctx,
        network=_StubNetwork(u0),
        model_step=toy_step,
        refine_steps=15,
        starts=F1_STARTS,
    )
    targets = np.asarray(jax.vmap(fwd)(jnp.asarray(u0)))
    assert est.pair_index(targets).tolist() == [0, 1]
    lm = est.estimate_counted(targets)[4]
    assert lm.start_selected.tolist() == [0, 0]
    assert not lm.start_material.any()
    assert est.start_record()["lm_start_switched"] == 0


def test_switch_off_never_enters_the_multi_start_code(monkeypatch) -> None:
    """With ``("network",)`` the estimator builds the single-start function.

    Reference: ``_build_multi`` is replaced by a function that raises, so any
    use of it fails the test. The single-start function is the one that
    ``test_estimation.py::test_l4_no_number_changes_bitwise_against_the_pre_
    change_function`` compares bitwise with a verbatim copy of the old code;
    this test shows the switch keeps the frozen systems on it. It also checks
    that the default is the single start, and that no tally is kept. The
    frozen run itself is checked by the WU-0039 smoke leafdiff. Tolerance:
    none.
    """

    def refuse(self):
        raise AssertionError("the multi-start code was entered")

    monkeypatch.setattr(StateEstimator, "_build_multi", refuse)
    targets = _noisy_targets(4, seed=3903)
    u0 = _starts()[:4]
    default = StateEstimator(
        ctx=_toy()[3],
        network=_StubNetwork(u0),
        model_step=toy_step,
        refine_steps=15,
    )
    assert default.starts == SINGLE_START == ("network",)
    explicit = _estimator(u0, SINGLE_START)
    out_default = default.estimate_counted(targets)
    out_explicit = explicit.estimate_counted(targets)
    for a, b in zip(out_default[:4], out_explicit[:4]):
        assert a.tobytes() == b.tobytes()
    assert out_default[4].start_selected is None
    assert out_default[4].start_material is None
    assert default.start_counts == {} and explicit.start_counts == {}
    multi = _estimator(u0, F1_STARTS)
    with pytest.raises(AssertionError, match="multi-start"):
        multi.estimate_counted(targets)


def test_frozen_and_unfixed_systems_keep_the_single_start() -> None:
    """Only S2, S4, S5 and S6 set F1; no system sets F2 (off by default).

    Reference: the brief of the V7 diagnosis (note 2026-10-25, section 6
    item 1), typed here. Tolerance: none.
    """
    fixed = {"lorenz63_r166", "hindmarsh_rose", "hyper_jha", "lorenz96_4"}
    for name, spec in SYSTEMS.items():
        expected = F1_STARTS if name in fixed else SINGLE_START
        assert spec.estimator_starts == expected, name
    assert F1_STARTS == ("network", "pair")
    assert F2_STARTS == ("network", "pair", "continuation")


def test_pair_index_equals_a_brute_force_argmin() -> None:
    """The nearest training pair equals the argmin of squared distances.

    Reference: the full distance matrix in NumPy and ``np.argmin`` (an
    exhaustive search, independent of the k-d tree). Continuous random data
    have no exact ties, and the gap between the nearest and the second
    nearest is checked to be well above round-off (``1e-9`` relative), so
    the argmin is unique. Tolerance: none (integer indices).
    """
    rng = np.random.default_rng(3904)
    pool = rng.standard_normal((2000, EMBED))
    queries = rng.standard_normal((300, EMBED))
    ctx = SimpleNamespace(
        embed_dim=EMBED,
        estimator_inputs=pool,
        estimator_targets=np.zeros((2000, 2)),
    )
    est = StateEstimator(
        ctx=ctx, network=None, model_step=None, starts=F1_STARTS
    )
    dist = np.sum((queries[:, None, :] - pool[None, :, :]) ** 2, axis=2)
    expected = np.argmin(dist, axis=1)
    ordered = np.sort(dist, axis=1)
    assert (ordered[:, 1] - ordered[:, 0] > 1e-9 * ordered[:, 1]).all()
    got = est.pair_index(queries)
    assert got.dtype == np.int64
    assert (got == expected).all()
    # The tree is built once and reused: a second call gives the same rows.
    tree = est._tree
    assert (est.pair_index(queries[:10]) == expected[:10]).all()
    assert est._tree is tree
    bad = queries[:3].copy()
    bad[1, 2] = np.nan
    with pytest.raises(ValueError, match="not finite"):
        est.pair_index(bad)
    with pytest.raises(ValueError, match="must be"):
        est.pair_index(queries[:, :5])


def test_continuation_ignores_the_newest_coordinate_bitwise() -> None:
    """The F2 stages never read the newest delay coordinate.

    Reference: construction. The stages fit the ``j`` oldest coordinates for
    ``j = m + 1, ..., D - 1`` (here 3 to 6 of 7), so the newest coordinate
    ``X[0]`` is masked out of the residual and the Jacobian in every stage
    (multiplied by an exact 0). Changing it by ``+5`` must leave the result
    bitwise unchanged. With ``D <= m + 1`` there is no stage and the start is
    returned unchanged. The stages move a wrong-basin start (a sanity check
    that they act at all). Tolerance: none.
    """
    ctx = _toy()[3]
    est = _estimator(_starts(), F2_STARTS)
    settle = jax.jit(est.continuation())
    target = _noisy_targets(1, seed=3905)[0]
    moved = target.copy()
    moved[0] += 5.0
    u0 = jnp.asarray([0.3, -1.4])
    u_a, cost_a, jac_a = settle(u0, jnp.asarray(target))
    u_b, _, _ = settle(u0, jnp.asarray(moved))
    assert np.asarray(u_a).tobytes() == np.asarray(u_b).tobytes()
    assert not bool(cost_a) and not bool(jac_a)
    assert np.asarray(u_a).tobytes() != np.asarray(u0).tobytes()
    short = SimpleNamespace(**{**vars(ctx), "embed_dim": 3, "history": 2})
    short_est = StateEstimator(
        ctx=short,
        network=None,
        model_step=toy_step,
        refine_steps=15,
        starts=F2_STARTS,
    )
    u_s, _, _ = jax.jit(short_est.continuation())(u0, jnp.asarray(target[:3]))
    assert np.asarray(u_s).tobytes() == np.asarray(u0).tobytes()


def test_f2_keeps_the_global_minimum_and_counts_three_starts() -> None:
    """F2 (three starts) also keeps the global minimum on the toy problem.

    Reference: the grid scan of the first test (global minimum near
    ``y = 1``). Tolerance: as in that test.
    """
    targets = _noisy_targets(6, seed=3901)
    est = _estimator(_starts(), F2_STARTS)
    states, _, _, _, lm = est.estimate_counted(targets)
    y = states[:, 1] / DECAY ** (EMBED - 1)
    for row, target in enumerate(targets):
        ys, costs = _grid_minima(target)
        best = int(np.argmin(costs))
        assert costs[best] - 1e-7 <= lm.residual[row] <= costs[best] + 1e-12
        assert abs(y[row] - ys[best]) <= GRID_STEP
    record = est.start_record()
    assert record["starts"] == ["network", "pair", "continuation"]
    assert sum(record["selected"].values()) == record["estimates"] == 6
    assert set(lm.start_selected.tolist()) <= {0, 1, 2}


@pytest.mark.parametrize("starts", [F1_STARTS, F2_STARTS])
def test_nonfinite_events_of_every_start_are_counted(starts) -> None:
    """A model that returns NaN sets both flags; the network is kept.

    Reference: construction (``s * nan``): every cost is mapped to ``inf``
    and every Jacobian entry is not finite, in every start and stage. All
    costs tie at ``inf``, so the network start is kept and no switch is
    material. Tolerance: none.
    """
    ctx = _toy()[3]
    u0 = _starts()[:3]
    est = StateEstimator(
        ctx=ctx,
        network=_StubNetwork(u0),
        model_step=lambda s: s * jnp.nan,
        refine_steps=15,
        starts=starts,
    )
    targets = _noisy_targets(3, seed=3906)
    _, _, state_replaced, _, lm = est.estimate_counted(targets)
    assert lm.nonfinite_cost.all() and lm.nonfinite_jacobian.all()
    assert np.isinf(lm.residual).all()
    assert lm.start_selected.tolist() == [0, 0, 0]
    assert not lm.start_material.any()
    assert state_replaced.all()


def test_bad_starts_raise() -> None:
    """Invalid start tuples, and several starts without a fit, are refused.

    Reference: the rules of ``check_starts``. Tolerance: none.
    """
    for bad in [(), ("pair", "network"), ("network", "network")]:
        with pytest.raises(ValueError):
            check_starts(bad)
    with pytest.raises(ValueError, match="unknown"):
        check_starts(("network", "analog"))
    with pytest.raises(ValueError, match="tuple"):
        check_starts(["network", "pair"])
    assert check_starts(F2_STARTS) is F2_STARTS
    with pytest.raises(ValueError, match="refine_steps"):
        StateEstimator(
            ctx=None,
            network=None,
            model_step=None,
            refine_steps=0,
            starts=F1_STARTS,
        )
    with pytest.raises(ValueError, match="first start"):
        SystemSpec(
            name="bad",
            field_fn=lorenz63_field,
            params={},
            dim=3,
            observed_index=0,
            initial_state=(1.0, 1.0, 1.0),
            max_dt=0.01,
            orbit_bound=40.0,
            estimator_starts=("pair",),
        )


def test_handling_reports_the_tallies_of_multi_start_systems_only(
    tmp_path,
) -> None:
    """``lm_starts`` appears for a multi-start system and nowhere else.

    Reference: the setups put in the study by hand, with tallies set by
    construction: the main setup of ``lorenz63_r166`` goes to the system
    block, its misspecified variant to the robustness block, and the
    single-start ``lorenz63`` gets no key (its handling is bitwise as
    before). Tolerance: none.
    """
    study = Study(StudyConfig(), tmp_path)
    dim = study.config.embedding_dim
    multi = _estimator(_starts(), F1_STARTS)
    multi.start_counts.update(
        {
            "estimates": 10,
            "selected/network": 7,
            "selected/pair": 3,
            "lm_start_switched": 3,
            "lm_start_switched_material": 2,
        }
    )
    variant = _estimator(_starts(), F1_STARTS)
    single = _estimator(_starts(), SINGLE_START)
    main_key = ("lorenz63_r166", dim, 5, 0.01, 0.0, 1)
    variant_key = ("lorenz63_r166", dim, 5, 0.01, 0.05, 1)
    study._setups = {
        main_key: SimpleNamespace(estimator=multi),
        variant_key: SimpleNamespace(estimator=variant),
        ("lorenz63", dim, 5, 0.01, 0.0, 1): SimpleNamespace(estimator=single),
    }
    block = study.system_handling("lorenz63_r166", {})
    assert block["lm_starts"] == {
        str(main_key): {
            "starts": ["network", "pair"],
            "estimates": 10,
            "selected": {"network": 7, "pair": 3},
            "lm_start_switched": 3,
            "lm_start_switched_material": 2,
        }
    }
    robust = study.robustness_handling("lorenz63_r166", {})
    assert list(robust["lm_starts"]) == [str(variant_key)]
    assert robust["lm_starts"][str(variant_key)]["estimates"] == 0
    assert "lm_starts" not in study.system_handling("lorenz63", {})
    assert "lm_starts" not in study.robustness_handling("lorenz63", {})
