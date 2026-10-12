"""Tests for lpcstudy.estimation: the replacements of ``StateEstimator`` are counted (DEF-0001)
and the Levenberg-Marquardt loop reports its residual and accepted steps (WU-0005.4, NVVUQ.10)."""

from __future__ import annotations

import functools
import math
from types import SimpleNamespace

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy.dynamics import delay_map_forward, make_observability
from lpcstudy.estimation import GOF_EXCEED, LMDiagnostics, StateEstimator, gof_threshold, lm_summary
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory

STATE_MEAN = np.array([0.5, -1.0, 8.0])


def _zero_lm(n: int) -> LMDiagnostics:
    """Diagnostics of a stub: nothing happened."""
    return LMDiagnostics(residual=np.zeros(n), accepted=np.zeros(n, dtype=np.int32),
                         nonfinite_cost=np.zeros(n, dtype=bool),
                         nonfinite_jacobian=np.zeros(n, dtype=bool),
                         late_progress=np.zeros(n, dtype=np.int32))


def _estimator(states: np.ndarray, nu: np.ndarray) -> StateEstimator:
    """An estimator whose compiled function is a stub returning fixed arrays (no network)."""
    return StateEstimator(ctx=SimpleNamespace(state_mean=STATE_MEAN), network=None,
                          model_step=None, _fn=lambda inputs: (states, nu, _zero_lm(len(states))))


def _old_replacements(states: np.ndarray, nu: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The two ``np.where`` lines of ``StateEstimator.estimate`` before WU-0002.11a, verbatim."""
    nu = np.where(np.isfinite(nu), nu, 1e6)
    states = np.where(np.isfinite(states), states, STATE_MEAN)
    return states, nu


def test_estimate_counted_a1_one_nan_state_one_inf_nu() -> None:
    """A1: one row with a NaN coordinate and one with nu = inf give one count each.

    Reference: a hand stub. Row 0 is finite; row 1 has one NaN coordinate; row 2 has nu = +inf.
    The expected counts are read off the construction (1 and 1). Values are compared bitwise
    (``tobytes``) with the two ``np.where`` lines of the code before the change, copied above:
    exact equality, because the new code applies the same expressions in the same order.
    """
    states = np.array([[1.0, 2.0, 3.0], [1.0, np.nan, 3.0], [4.0, 5.0, 6.0]])
    nu = np.array([2.0, 3.0, np.inf])
    est = _estimator(states, nu)
    got_states, got_nu, state_replaced, nu_replaced, _ = est.estimate_counted(np.zeros((3, 7)))
    ref_states, ref_nu = _old_replacements(states, nu)
    assert got_states.tobytes() == ref_states.tobytes()
    assert got_nu.tobytes() == ref_nu.tobytes()
    assert int(state_replaced.sum()) == 1 and state_replaced.tolist() == [False, True, False]
    assert int(nu_replaced.sum()) == 1 and nu_replaced.tolist() == [False, False, True]
    assert got_states[1].tolist() == [1.0, STATE_MEAN[1], 3.0] and got_nu[2] == 1e6


def test_estimate_counts_estimates_not_coordinates() -> None:
    """The unit is one estimate: two bad coordinates in a row count once, and a row can be in both.

    Reference: hand stub. Row 0: NaN and +inf coordinates and nu = NaN (one state replacement and
    one nu replacement). Row 1: all three coordinates -inf (one state replacement). Row 2: finite
    state, nu = -inf (one nu replacement; ``isfinite`` is False for -inf). Expected 2 and 2,
    by construction.
    """
    states = np.array([[np.nan, np.inf, 1.0], [-np.inf, -np.inf, -np.inf], [0.0, 0.0, 0.0]])
    nu = np.array([np.nan, 1.0, -np.inf])
    got_states, got_nu, state_replaced, nu_replaced, _ = _estimator(states, nu).estimate_counted(
        np.zeros((3, 7)))
    assert int(state_replaced.sum()) == 2 and int(nu_replaced.sum()) == 2
    assert state_replaced.tolist() == [True, True, False]
    assert nu_replaced.tolist() == [True, False, True]
    ref_states, ref_nu = _old_replacements(states, nu)
    assert got_states.tobytes() == ref_states.tobytes() and got_nu.tobytes() == ref_nu.tobytes()


def test_estimate_delegates_to_estimate_counted() -> None:
    """``estimate`` returns exactly the first two outputs of ``estimate_counted``.

    Reference: the old ``estimate`` lines (copied) on a stub with a NaN state and an infinite nu;
    bitwise equality, since the same expressions run.
    """
    states = np.array([[1.0, np.nan, 3.0], [4.0, 5.0, 6.0]])
    nu = np.array([np.inf, 2.0])
    est = _estimator(states, nu)
    plain_states, plain_nu = est.estimate(np.zeros((2, 7)))
    ref_states, ref_nu = _old_replacements(states, nu)
    assert plain_states.tobytes() == ref_states.tobytes() and plain_nu.tobytes() == ref_nu.tobytes()


# ---------------------------------------------------------------------------------------------
# WU-0005.4: Levenberg-Marquardt diagnostics (NVVUQ.10). The test world is built by hand: Lorenz-63
# flow map at a fixed interval, D = 7, identity whitening, mean 0, a stub network returning the
# chosen start. Data come from literal ``np.random.default_rng(<int>)`` (development, not a study
# seed). The truth of every case is an independent simulation, never the code under test.
# ---------------------------------------------------------------------------------------------
EMBED = 7
INTERVAL = 1.0 / (30 * 0.9056)
N_ROWS = 32


class _StubNetwork:
    """A network whose ``predict`` returns the start ``u0`` the test sets."""

    width = 0

    def __init__(self) -> None:
        self.u0: np.ndarray | None = None

    def predict(self, inputs):
        return jnp.asarray(self.u0)


@functools.lru_cache(maxsize=None)
def _world(tau: int):
    """Flow map, attractor trajectory, context and normalized observations for delay ``tau``.

    The trajectory is simulated with ``simulate_trajectory`` (the same ``step`` object as the
    estimator, i.e. the same discrete map, LPC.NV.1) after a burn-in of 3000 steps, so the states
    are on the attractor. ``obs_mean`` and ``obs_scale`` are the mean and standard deviation of x
    on it, so the normalized observations are O(1).
    """
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, INTERVAL)
    span = (EMBED - 1) * tau
    burn = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)
    traj = simulate_trajectory(step, jnp.asarray(burn[-1]), 600 + span + 1)
    mean, scale = float(traj[:, 0].mean()), float(traj[:, 0].std())
    ctx = SimpleNamespace(unwhiten=np.eye(3), whiten=np.eye(3), state_mean=np.zeros(3),
                          spec=SimpleNamespace(observed_index=0), obs_mean=mean, obs_scale=scale,
                          delay=tau, embed_dim=EMBED, history=span)
    return step, traj, ctx


def _cases(tau: int, n: int = N_ROWS, seed: int = 20261011):
    """Window-start states and their clean normalized delay vectors, from the trajectory.

    The delay vector of the window starting at index ``i`` is the observation at
    ``i + (D - 1 - j) tau``, ``j = 0..D-1`` (newest first), read off the simulated trajectory.
    """
    _, traj, ctx = _world(tau)
    starts = np.random.default_rng(seed).choice(600, size=n, replace=False)
    obs = (traj[:, 0] - ctx.obs_mean) / ctx.obs_scale
    index = starts[:, None] + (EMBED - 1 - np.arange(EMBED))[None, :] * tau
    return traj[starts], obs[index]


@functools.lru_cache(maxsize=None)
def _shared(tau: int, steps: int):
    """One estimator per (delay, iterations) with its stub network and compiled trace.

    Cached so that the tests of one delay share the compilation of the loop; each test sets
    ``network.u0`` first. The trace is the test-only scan over the same step closure.
    """
    step, _, ctx = _world(tau)
    network = _StubNetwork()
    est = StateEstimator(ctx=ctx, network=network, model_step=step, refine_steps=steps)
    parts = est.refinement()
    return est, network, jax.jit(jax.vmap(parts.trace)), jax.jit(jax.vmap(parts.cost))


def _eta(x: np.ndarray) -> float:
    """Round-off bound of the residual (applied-mathematician M2/M3, WU-0005.4).

    1e-12 max(1, ||X||_inf), in normalized observation units: a bound on the difference between
    two XLA-CPU compilations of the same discrete map over a window of at most 1 Lyapunov time
    (random-walk estimate 1.5e-12 from sqrt(120) RK4 substeps x 4 ulp x |s| eps x tangent growth
    30; observed below 1e-15, so the bound is about 1e3 above what is seen).
    """
    return 1e-12 * max(1.0, float(np.max(np.abs(x))))


def _trace(tau: int, steps: int, u0: np.ndarray, x: np.ndarray):
    """Run the production estimator and the trace variant on the same inputs."""
    est, network, trace, cost = _shared(tau, steps)
    network.u0 = u0
    produced = est.estimate_counted(x)
    final, diag, (us, cs, accept) = trace(jnp.asarray(u0), jnp.asarray(x))
    c0 = np.asarray(cost(jnp.asarray(u0), jnp.asarray(x)))
    return (est, produced, np.asarray(final), tuple(np.asarray(d) for d in diag),
            np.asarray(us), np.asarray(cs), np.asarray(accept), c0)


def _expected_late(c0: np.ndarray, cs: np.ndarray, accept: np.ndarray, steps: int) -> np.ndarray:
    """``late_progress`` recomputed from a trace: a material accepted step in the last 3 iterations.

    Material means the cost fell by more than 1e-6 of the carried cost before the step, or the
    carried cost was infinite (a non-finite start left for a finite cost; R4).
    """
    prev = np.concatenate([c0[:, None], cs[:, :-1]], axis=1)
    material = accept & (((prev - cs) > 1e-6 * prev) | np.isinf(prev))  # inf - c is not > 1e-6 inf
    return material[:, max(0, steps - 3):].any(axis=1).astype(np.int32)


@pytest.mark.parametrize("tau", [2, 5])
def test_l1_true_start_no_noise_exact_model(tau: int) -> None:
    """L1 (ROADMAP verbatim): from the true state, no noise, exact model, the cost never rises.

    Reference: the target is the clean normalized delay vector read off an independently
    simulated trajectory (``simulate_trajectory``, not ``delay_map_forward``); the accept flags
    are counted from the trace variant, which is the same scan body with per-iteration outputs.
    (a) the carried cost is non-increasing at every iteration and strictly lower exactly where
    the accept flag is set (exact: the bookkeeping of the carry); (b) the production residual is
    at most D eta^2 with eta = 1e-12 max(1, ||X||_inf) (applied-mathematician M3: the expected
    value is about D (kappa eps |x|)^2 ~ 1e-28 and the observed maximum 5e-31, so the bound is
    more than 1e7 above round-off and still about 1e10 below the 1e-13..1e-12 an accidental
    float32 path would give); (c) the production ``accepted`` equals the test's count of accept
    flags and of strict decreases (exact); (d) the production final state, residual and flags
    equal the trace's bitwise: two programs of one body doing the same float arithmetic. A
    mismatch of (d) would be a finding, never a tolerance. Both branches occur: with 32 states
    some iterations accept and some reject at the truth, where the decision is made by ulps.
    """
    truth, x = _cases(tau)
    est, produced, final, diag, us, cs, accept, c0 = _trace(tau, 15, truth, x)
    states, _, _, _, lm = produced
    prev = np.concatenate([c0[:, None], cs[:, :-1]], axis=1)
    assert np.all(cs <= prev)  # (a)
    assert np.array_equal(cs < prev, accept)
    assert accept.any() and (~accept).any()
    bound = len(x[0]) * _eta(x) ** 2
    assert np.all(lm.residual <= bound)  # (b)
    assert np.array_equal(lm.accepted, accept.sum(axis=1))  # (c)
    assert np.array_equal(lm.accepted, (cs < prev).sum(axis=1))
    step, _, ctx = _world(tau)
    root, mean = jnp.asarray(ctx.unwhiten), jnp.asarray(ctx.state_mean)
    advance = jax.jit(jax.vmap(lambda u: jax.lax.fori_loop(
        0, ctx.history, lambda _, s: step(s), mean + root @ u)))
    assert states.tobytes() == np.asarray(advance(jnp.asarray(final))).tobytes()  # (d)
    assert lm.residual.tobytes() == diag[0].tobytes()
    assert np.array_equal(lm.accepted, diag[1]) and np.array_equal(lm.late_progress, diag[4])
    assert not lm.nonfinite_cost.any() and not lm.nonfinite_jacobian.any()


def test_l2_perturbed_start_cost_matches_independent_recomputation() -> None:
    """L2: from u_true + delta (|delta| = 0.01), no noise, the loop converges and the cost is true.

    Reference: J(u) = ||X - G(u)||^2 recomputed by a separately compiled ``jit(vmap(...))`` of
    ``delay_map_forward`` called outside the loop. For each accepted iterate (and for the start):
    |c_k - J(u_k)| <= eta (2 sqrt(J) + eta) with eta = 1e-12 max(1, ||X||_inf). Derivation: with e the
    difference of the two residual vectors, |c - J| = | ||r||^2 - ||r + e||^2 | <= ||e|| (2 sqrt(J) +
    ||e||), and ||e|| <= eta is the round-off bound of ``_eta`` (a relative bound 1e-12 J would be
    invalid, because J falls to about 1e-31 where one ulp of e is order 1 relatively).
    The iterates are non-increasing in J up to the two bounds: J_k <= J_{k-1} + b_k + b_{k-1}
    with b = eta (2 sqrt(J) + eta). ``accepted >= 1`` and the final residual <= D eta^2 (M3).
    delta is 10 to 50 times inside the Gauss-Newton basin edge (probe: 64 of 64 states converge
    at |delta| = 0.01, tau = 5, 15 iterations; the edge is at about 0.5). ``refine_steps = 15`` is
    explicit (the dataclass default is 6). ``late_progress`` equals its recomputation from the trace.
    """
    tau, steps = 5, 15
    truth, x = _cases(tau)
    direction = np.random.default_rng(7).standard_normal(truth.shape)
    u0 = truth + 0.01 * direction / np.linalg.norm(direction, axis=1, keepdims=True)
    est, produced, _, _, us, cs, accept, c0 = _trace(tau, steps, u0, x)
    lm = produced[4]
    step, _, ctx = _world(tau)
    fwd = delay_map_forward(step, 0, ctx.obs_mean, ctx.obs_scale, tau, EMBED)
    independent = jax.jit(jax.vmap(lambda u, target: jnp.sum((target - fwd(u)) ** 2)))
    eta = _eta(x)
    j_start = np.asarray(independent(jnp.asarray(u0), jnp.asarray(x)))
    j_all = np.stack([np.asarray(independent(jnp.asarray(us[:, k]), jnp.asarray(x)))
                      for k in range(steps)], axis=1)

    def bound(j: np.ndarray) -> np.ndarray:
        return eta * (2.0 * np.sqrt(j) + eta)

    assert np.all(np.abs(c0 - j_start) <= bound(j_start))
    assert np.all((np.abs(cs - j_all) <= bound(j_all))[accept])
    j_prev = np.concatenate([j_start[:, None], j_all[:, :-1]], axis=1)
    assert np.all((j_all <= j_prev + bound(j_all) + bound(j_prev))[accept])
    assert np.all(lm.accepted >= 1)
    assert np.all(lm.residual <= EMBED * eta**2)
    assert np.array_equal(lm.late_progress, _expected_late(c0, cs, accept, steps))


def test_late_progress_flags_unconverged_estimates() -> None:
    """D1: ``late_progress`` is 1 exactly when a material accepted step falls in the last 3 iterations.

    Reference: the flag recomputed by the test from the trace variant (accept flags and carried
    costs, relative decrease > 1e-6), on two runs: 3 iterations from a start 0.1 away (the loop is
    still moving, so many flags are 1) and 15 iterations from 0.01 away (converged, so the flags
    are 0). Exact equality of the integer arrays; both values must occur across the two runs.
    """
    tau = 5
    truth, x = _cases(tau)
    seen = set()
    for steps, size in ((3, 0.1), (15, 0.01)):
        direction = np.random.default_rng(11).standard_normal(truth.shape)
        u0 = truth + size * direction / np.linalg.norm(direction, axis=1, keepdims=True)
        _, produced, _, _, _, cs, accept, c0 = _trace(tau, steps, u0, x)
        expected = _expected_late(c0, cs, accept, steps)
        assert np.array_equal(produced[4].late_progress, expected)
        seen |= set(expected.tolist())
    assert seen == {0, 1}


def test_late_progress_counts_a_first_accept_from_a_nonfinite_start() -> None:
    """R4 and R7: leaving an infinite cost for a finite one in the last iterations sets the flag.

    Reference: construction. The model step is the identity, so G(u) = (u_0 - mean)/sigma for every
    delay and the objective is a parabola in u_0 alone. Row 0 starts at u_0 = 2e155: the residual is
    about 2.5e154 (sigma_x = 7.9) and its square overflows 1.8e308, so the start cost is inf
    (``nonfinite_cost`` True) while the Jacobian and the right-hand side are finite; the damped step
    (damping 1e-3) removes 99.97% of u_0, the candidate cost is about 5e302 and finite, and it is
    accepted from an infinite carried cost, where ``inf - c > 1e-6 inf`` is False in
    floating point. With ``refine_steps = 1`` the single iteration is the inf -> finite accept, so
    it is the only candidate for the flag: the rule before the fix, ``c_u - c_cand > 1e-6 c_u``,
    gives False (inf > inf), and the rule with the ``isinf(c_u)`` term gives True; this is asserted
    from the trace, and the production flag must be 1 (it would be 0 before the fix; with 3
    iterations the later accepts, with relative decrease ~1 - 1e-8, would have set it under the old
    rule too, R7). The expected flag is 1 by the definition (a finite step out of an infinite cost
    is unboundedly material). Row 1 starts at the minimum (cost exactly 0, nothing can be
    accepted): flag 0, accepted 0. Exact.
    """
    ctx = _world(1)[2]
    network = _StubNetwork()
    network.u0 = np.array([[2e155, 0.0, 0.0], [ctx.obs_mean, 0.0, 0.0]])
    est = StateEstimator(ctx=ctx, network=network, model_step=lambda s: s, refine_steps=1)
    x = np.zeros((2, EMBED))
    *_, lm = est.estimate_counted(x)
    assert lm.nonfinite_cost.tolist() == [True, False]
    assert lm.accepted.tolist() == [1, 0] and np.isfinite(lm.residual[0])
    assert 1e300 < lm.residual[0] < 1e305 and lm.residual[1] == 0.0
    assert lm.late_progress.tolist() == [1, 0]
    # The old rule on the same inputs, from the trace: the carried cost before the step is inf and
    # the one after is finite, so `c_u - c_cand > 1e-6 c_u` is False (the test discriminates).
    parts = est.refinement()
    _, _, (_, cs, accept) = jax.jit(jax.vmap(parts.trace))(jnp.asarray(network.u0),
                                                           jnp.asarray(x))
    c0 = np.asarray(jax.jit(jax.vmap(parts.cost))(jnp.asarray(network.u0), jnp.asarray(x)))
    cs, accept = np.asarray(cs), np.asarray(accept)
    assert np.isinf(c0[0]) and np.isfinite(cs[0, 0]) and accept[0, 0]
    assert not (c0[0] - cs[0, 0] > 1e-6 * c0[0])  # the pre-fix expression
    assert np.array_equal(_expected_late(c0, cs, accept, 1), [1, 0])  # with the isinf term


def test_l3_nonfinite_target_row_is_counted_per_estimate() -> None:
    """L3(i): a NaN in one row's target gives S3 for that row only.

    Reference: construction. Row 0 is finite and started 0.01 from the truth; row 1 has a NaN in
    its target and starts at the truth. The Jacobian does not depend on the target, so
    ``nonfinite_jacobian`` is False for both rows. Row 1: the start cost is NaN, mapped to inf
    (``nonfinite_cost`` True), the right-hand side is NaN, every candidate cost is inf and none is
    accepted: ``accepted`` 0, residual inf, and the carried state is the start (finite), so
    nothing is replaced downstream. Row 0: no flag, a finite residual, at least one accept. Exact.
    """
    tau = 2
    truth, x = _cases(tau, n=2)
    x = x.copy()
    x[1, 3] = np.nan
    u0 = truth.copy()
    u0[0] = u0[0] + 0.01 * np.array([1.0, -1.0, 1.0]) / np.sqrt(3.0)
    est = StateEstimator(ctx=_world(tau)[2], network=_StubNetwork(), model_step=_world(tau)[0],
                         refine_steps=15)
    est.network.u0 = u0
    _, _, replaced_state, _, lm = est.estimate_counted(x)
    assert lm.nonfinite_cost.tolist() == [False, True]
    assert lm.nonfinite_jacobian.tolist() == [False, False]
    assert lm.accepted[1] == 0 and np.isinf(lm.residual[1])
    assert np.isfinite(lm.residual[0]) and lm.accepted[0] >= 1
    assert not replaced_state.any()


def test_l3_nan_model_counts_every_estimate_in_both_counters() -> None:
    """L3(ii): a model step that returns NaN makes every estimate non-finite in cost and Jacobian.

    Reference: construction, with the stub ``lambda s: s * jnp.nan`` (the forward-mode tangent of
    ``full_like(s, nan)`` or of ``s + nan`` is finite, so those stubs would not exercise S4;
    applied-mathematician L3(ii): 18 of 21 Jacobian entries are non-finite with ``s * nan``, row 0
    is the observation of the start state and stays finite). Every cost is inf, every Jacobian
    has zeroed entries, the right-hand side is NaN, so no step is accepted: ``accepted`` 0 and
    residual inf for all n estimates. The advanced state is NaN, so ``state_replaced`` is True for
    all n (``invariant_mean_replacements`` = n). All exact.
    """
    ctx = _world(1)[2]
    n = 3
    u0 = np.array([[1.0, 2.0, 3.0], [-1.0, 0.5, 2.0], [4.0, -3.0, 20.0]])
    network = _StubNetwork()
    network.u0 = u0
    est = StateEstimator(ctx=ctx, network=network, model_step=lambda s: s * jnp.nan,
                         refine_steps=4)
    states, nu, state_replaced, nu_replaced, lm = est.estimate_counted(np.full((n, EMBED), 0.5))
    assert lm.nonfinite_cost.all() and lm.nonfinite_jacobian.all()
    assert np.all(lm.accepted == 0) and np.all(np.isinf(lm.residual))
    assert int(state_replaced.sum()) == n and int(nu_replaced.sum()) == n
    assert np.all(states == ctx.state_mean) and np.all(nu == 1e6)


def test_zero_refine_steps_defines_the_diagnostics() -> None:
    """``refine_steps = 0``: residual = cost at the start, accepted 0, no flags, state = start.

    Reference: J(u0) = ||X - G(u0)||^2 from a separately compiled ``delay_map_forward``; the
    states equal the start advanced over the window, by the same expression as the old code
    (``u = u0`` when refinement is disabled). Tolerance: the two residual computations are two
    compilations of the same map, so eta (2 sqrt(J) + eta) as in L2 with J of order 1e-4.
    Exact for the integer and boolean fields and the states.
    """
    tau = 2
    truth, x = _cases(tau, n=8)
    direction = np.random.default_rng(5).standard_normal(truth.shape)
    u0 = truth + 0.05 * direction / np.linalg.norm(direction, axis=1, keepdims=True)
    step, _, ctx = _world(tau)
    network = _StubNetwork()
    network.u0 = u0
    est = StateEstimator(ctx=ctx, network=network, model_step=step, refine_steps=0)
    states, _, _, _, lm = est.estimate_counted(x)
    fwd = delay_map_forward(step, 0, ctx.obs_mean, ctx.obs_scale, tau, EMBED)
    j_start = np.asarray(jax.jit(jax.vmap(lambda u, t: jnp.sum((t - fwd(u)) ** 2)))(
        jnp.asarray(u0), jnp.asarray(x)))
    eta = _eta(x)
    assert np.all(np.abs(lm.residual - j_start) <= eta * (2.0 * np.sqrt(j_start) + eta))
    assert np.all(lm.accepted == 0) and not lm.nonfinite_cost.any()
    assert not lm.nonfinite_jacobian.any() and np.all(lm.late_progress == 0)
    advance = jax.jit(jax.vmap(lambda s: jax.lax.fori_loop(0, ctx.history, lambda _, v: step(v), s)))
    assert states.tobytes() == np.asarray(advance(jnp.asarray(u0))).tobytes()


def _reference_run(est: StateEstimator):
    """The compiled function of ``StateEstimator._build`` before WU-0005.4, copied verbatim.

    Only ``self`` is renamed ``est``; the body is that of commit 221ae9a (the base of the branch).
    It returns ``(states, nu)`` without the replacements, exactly as the old compiled function.
    """
    self = est
    ctx = self.ctx
    root = jnp.asarray(ctx.unwhiten)
    mean = jnp.asarray(ctx.state_mean)
    fwd = delay_map_forward(self.model_step, ctx.spec.observed_index, ctx.obs_mean,
                            ctx.obs_scale, ctx.delay, ctx.embed_dim)
    span = ctx.history
    step = self.model_step
    nu_fn = make_observability(step, ctx.spec.observed_index, ctx.obs_scale,
                               ctx.whiten, ctx.delay, ctx.embed_dim)
    n_iter = self.refine_steps

    def generate(u: jnp.ndarray) -> jnp.ndarray:
        return fwd(mean + root @ u)

    jac = jax.jacfwd(generate)

    def cost(u: jnp.ndarray, target: jnp.ndarray) -> jnp.ndarray:
        resid = target - generate(u)
        value = jnp.sum(resid**2)
        return jnp.where(jnp.isfinite(value), value, jnp.inf)

    def refine(u0: jnp.ndarray, target: jnp.ndarray) -> jnp.ndarray:
        dim = u0.shape[0]

        def body(carry, _):
            u, c_u, damping = carry
            a_mat = jac(u)
            a_mat = jnp.where(jnp.isfinite(a_mat), a_mat, 0.0)
            normal = a_mat.T @ a_mat
            rhs = a_mat.T @ (target - generate(u))
            scale = jnp.trace(normal) / dim + 1e-12
            delta = jnp.linalg.solve(normal + damping * scale * jnp.eye(dim), rhs)
            cand = u + delta
            c_cand = cost(cand, target)
            accept = c_cand < c_u
            u_new = jnp.where(accept, cand, u)
            return (u_new, jnp.where(accept, c_cand, c_u),
                    jnp.where(accept, damping / 3.0, damping * 4.0)), None

        (u_final, _, _), _ = jax.lax.scan(body, (u0, cost(u0, target), 1e-3), None,
                                          length=n_iter)
        return u_final

    def advance(s_old: jnp.ndarray) -> jnp.ndarray:
        return jax.lax.fori_loop(0, span, lambda _, s: step(s), s_old)

    def single(x: jnp.ndarray, u0: jnp.ndarray) -> tuple[jnp.ndarray, jnp.ndarray]:
        u = refine(u0, x) if n_iter > 0 else u0
        s_old = mean + root @ u
        return advance(s_old), s_old

    batched = jax.jit(jax.vmap(single))

    def run(inputs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        u0 = jnp.asarray(self.network.predict(jnp.asarray(inputs)))
        s_t, s_old = batched(jnp.asarray(inputs), u0)
        nu = nu_fn(s_old)
        return np.asarray(s_t), np.asarray(nu)

    return run


def _assert_same_estimates(est: StateEstimator, x: np.ndarray) -> None:
    """The new ``estimate_counted`` values equal the pre-change function plus its replacements."""
    ref_states, ref_nu = _reference_run(est)(x)
    ref_states, ref_nu = _old_replacements_for(est, ref_states, ref_nu)
    states, nu, *_ = est.estimate_counted(x)
    assert states.tobytes() == ref_states.tobytes() and nu.tobytes() == ref_nu.tobytes()


def _old_replacements_for(est: StateEstimator, states: np.ndarray, nu: np.ndarray):
    """The two ``np.where`` replacement lines of the old ``estimate_counted``, with the context mean."""
    return (np.where(np.isfinite(states), states, est.ctx.state_mean),
            np.where(np.isfinite(nu), nu, 1e6))


def test_l4_no_number_changes_bitwise_against_the_pre_change_function() -> None:
    """L4: the estimates and nu are bitwise those of the function before the change.

    Reference: ``_reference_run``, the old compiled function copied verbatim (regression guard,
    not correctness evidence: it shows that adding the diagnostics changed no bit). 32 noisy
    inputs (rho = 0.01 of sigma_x; the observations are normalized by sigma_x so the noise sd is
    0.01); starts u_true + 0.02 N(0, I) except eight rows (the first eight) started exactly at
    u_true, where the accept decisions are ties decided by ulps and any re-fusion of the compiled
    loop shows first. A failure is a finding about XLA fusion, never a tolerance. A second call
    uses the NaN-stub model (``s * nan``), so the rebound ``isfinite`` mask path and the
    replacements are covered: the replaced states and nu are bitwise those of the old function.
    """
    tau = 5
    truth, x = _cases(tau)
    rng = np.random.default_rng(42)
    noisy = x + 0.01 * rng.standard_normal(x.shape)
    u0 = truth + 0.02 * rng.standard_normal(truth.shape)
    u0[:8] = truth[:8]
    est, network, *_ = _shared(tau, 15)
    network.u0 = u0
    _assert_same_estimates(est, noisy)
    ctx = _world(tau)[2]
    network_nan = _StubNetwork()
    network_nan.u0 = u0[:4]
    est_nan = StateEstimator(ctx=ctx, network=network_nan, model_step=lambda s: s * jnp.nan,
                             refine_steps=15)
    _assert_same_estimates(est_nan, noisy[:4])
    _, _, state_replaced, _, lm = est_nan.estimate_counted(noisy[:4])
    assert state_replaced.all() and lm.nonfinite_cost.all() and lm.nonfinite_jacobian.all()


def _chi2_survival(x: float, dof: int) -> float:
    """P(chi^2_dof > x) by the closed forms of the Erlang and half-integer gamma tails.

    Even dof: ``exp(-y) sum_{k < dof/2} y^k / k!``; odd dof, ``a = dof/2 = n + 1/2``:
    ``erfc(sqrt y) + exp(-y) sum_{k=1..n} y^(k - 1/2) / Gamma(k + 1/2)``; with ``y = x/2``.
    Standard identities of the regularized upper incomplete gamma function; ``math`` only,
    independent of scipy.
    """
    y = x / 2.0
    if dof % 2 == 0:
        return math.exp(-y) * sum(y**k / math.factorial(k) for k in range(dof // 2))
    n = (dof - 1) // 2
    return math.erfc(math.sqrt(y)) + math.exp(-y) * sum(
        y ** (k - 0.5) / math.gamma(k + 0.5) for k in range(1, n + 1))


@pytest.mark.parametrize("dof", [1, 2, 4, 7, 8])
def test_gof_threshold_is_the_chi2_999_quantile_for_any_dof(dof: int) -> None:
    """``gof_threshold(dof)`` is the root of P(chi^2_dof > x) = 0.001 (R2, D3, DEC-0025).

    Reference: bisection (200 steps on [0, 200]) of the closed-form survival function of
    ``_chi2_survival`` (dof 2: exp(-x/2); dof 4: exp(-x/2)(1 + x/2); dof 7 by the half-integer
    gamma identity), independent of scipy. Tolerance: relative 1e-10; the scipy quantile is good
    to about 1e-15 and the bisection to 1e-13, so the margin is above 1e3. For dof = 4 the value
    is also the 18.46682695290317 of the D = 7 report, unchanged (``GOF_EXCEED``); the hand values
    13.8155 (= 2 ln 1000) for dof 2 and 24.32 for dof 7 are checked to 4 digits.
    """
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if _chi2_survival(mid, dof) > 1e-3 else (lo, mid)
    assert gof_threshold(dof) == pytest.approx(0.5 * (lo + hi), rel=1e-10)
    if dof == 4:
        assert GOF_EXCEED == gof_threshold(4) and round(GOF_EXCEED, 4) == 18.4668
        assert GOF_EXCEED == 18.46682695290317
    if dof == 2:
        assert gof_threshold(2) == pytest.approx(2.0 * math.log(1000.0), rel=1e-12)
    if dof == 7:
        assert round(gof_threshold(7), 2) == 24.32
    for bad in (0, -1, 2.5):
        with pytest.raises(ValueError, match="positive integer"):
            gof_threshold(bad)


def _hand(values: list[float], iterations: list[int] | None = None, late: list[int] | None = None,
          noise: float = 0.1, dof: int = 4) -> dict:
    n = len(values)
    return lm_summary(np.array(values), np.array(iterations if iterations is not None else [3] * n),
                      np.array(late if late is not None else [0] * n), noise, dof)


@pytest.mark.parametrize("values, p95, median, infs", [
    (list(range(20)) + [np.inf], 19.0, 10.0, 1),            # n = 21: ceil(0.95 n) = 20, x_(20) = 19
    (list(range(18)) + [np.inf, np.inf], None, 9.5, 2),      # n = 20: x_(19) = inf, median (9+10)/2
    (list(range(19)) + [np.inf], 18.0, 9.5, 1),              # n = 20: x_(19) = 18, median (9+10)/2
    ([np.inf], None, None, 1),                               # a single inf
])
def test_l5_lm_summary_quantiles_with_infinities(values, p95, median, infs) -> None:
    """L5: the p95 is the order statistic x_(ceil(0.95 n)) and an infinite statistic is None.

    Reference: the order statistics by hand (closed form), with the linear quantile method
    ruled out because it returns NaN for a finite quantile next to an inf (applied-mathematician
    M5, measured with numpy 2.5.3). Values are small integers, so equality is exact. The count of
    infinite residuals is exact.
    """
    out = _hand([float(v) for v in values])
    assert out["n_estimates"] == len(values) and out["nonfinite_residuals"] == infs
    assert out["p95_residual"] == p95 and out["median_residual"] == median


def test_l5_lm_summary_other_keys_and_empty_and_errors() -> None:
    """L5: the other summary keys equal hand values, the empty case is all None, bad input raises.

    Reference: hand arrays. accepted = [0, 0, 3, 5, 15] has median 3 and two zeros of five, so
    ``fraction_no_decrease`` is 0.4; late = [1, 0, 0, 0, 1] gives 0.4. With noise 0.1 the
    threshold on c is 18.4668 * 0.01 = 0.1847: residuals [0.01, 0.1, 0.2, inf, 0.18] exceed it at
    0.2 and inf only, so 2 of 5 = 0.4 (0.18 is 1.5% below the threshold, far from the tie).
    Empty input: ``n_estimates`` 0, ``nonfinite_residuals`` 0 and the rest None. NaN, a size
    mismatch and a non-positive noise raise (no silent handling).
    """
    out = _hand([0.01, 0.1, 0.2, np.inf, 0.18], [0, 0, 3, 5, 15], [1, 0, 0, 0, 1])
    assert out["median_iterations"] == 3.0 and out["fraction_no_decrease"] == 0.4
    assert out["fraction_late_progress"] == 0.4 and out["fraction_above_chi2"] == 0.4
    assert out["median_residual"] == 0.18 and out["noise"] == 0.1 and out["nonfinite_residuals"] == 1
    empty = _hand([])
    assert empty["n_estimates"] == 0 and empty["nonfinite_residuals"] == 0
    assert all(empty[k] is None for k in ("median_residual", "p95_residual", "median_iterations",
                                          "fraction_no_decrease", "fraction_late_progress",
                                          "fraction_above_chi2"))
    with pytest.raises(ValueError, match="NaN"):
        _hand([1.0, np.nan])
    with pytest.raises(ValueError, match="sizes differ"):
        lm_summary(np.zeros(3), np.zeros(2), np.zeros(3), 0.1, 4)
    with pytest.raises(ValueError, match="positive"):
        _hand([1.0], noise=0.0)
    with pytest.raises(ValueError, match="degrees of freedom"):
        _hand([1.0], dof=0)


def test_lm_summary_threshold_follows_the_degrees_of_freedom() -> None:
    """R2: the fraction above the chi-square quantile uses the cell's dof, which is stored.

    Reference: hand fractions. noise 1.0 and residuals [13, 14, 19, 21, 25]. Thresholds
    (0.999 quantiles): dof 2: 13.82 (2 ln 1000), so 14, 19, 21, 25 exceed it: 0.8; dof 4: 18.47:
    19, 21, 25: 0.6; dof 7: 24.32: only 25: 0.2. The closest value to a threshold is 14
    against 13.82 (0.18 away), far above the round-off of the quantile (1e-15).
    ``gof_dof`` is stored. Exact (multiples of 1/5).
    """
    values = [13.0, 14.0, 19.0, 21.0, 25.0]
    got = {dof: _hand(values, noise=1.0, dof=dof) for dof in (2, 4, 7)}
    assert [got[d]["fraction_above_chi2"] for d in (2, 4, 7)] == [0.8, 0.6, 0.2]
    assert [got[d]["gof_dof"] for d in (2, 4, 7)] == [2, 4, 7]


# ------------------------------------------------ randomness of the networks (WU-0002.14, P7)
def _tiny_training_set() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(14007)
    inputs = rng.standard_normal((40, 2))
    targets = np.sin(inputs[:, :1]) + 0.5 * inputs[:, 1:]
    return inputs, targets


def test_train_mlp_draws_its_randomness_from_the_generator_in_the_documented_order(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """P7: equal generator states give identical networks; other labels give other ones; M7 order.

    Reference: a hand re-draw from ``np.random.default_rng([seed, crc32(label)])`` (NumPy used
    directly, independent of ``make_rng``): two 32-bit integers (the JAX keys: initialization,
    then the epoch stream), then ``permutation(n)`` for the validation split, then the validation
    input noise. The keys that ``train_mlp`` hands to ``jax.random.PRNGKey`` are recorded and
    must be those two integers; the reported ``val_loss`` is recomputed from the returned network
    on the hand-chosen validation rows and noise. Tolerance: none for the recorded keys, the
    parameters and the val_loss of two equal calls (the same deterministic XLA program on the same
    inputs, same process: bitwise); ``val_loss`` against the recomputation ``rel 1e-12`` (the
    same ``predict`` on the same inputs, a sum of 1 residual component per row: round-off only).
    A different label gives different parameters (checked as inequality of the first weight).
    """
    import zlib

    from lpcstudy import networks
    from lpcstudy.data import make_rng

    inputs, targets = _tiny_training_set()
    seed, label = 20261005, "lorenz63|7|5|estimator|0.01|32"

    def hand() -> np.random.Generator:
        return np.random.default_rng([seed, zlib.crc32(label.encode())])

    recorded: list[int] = []
    real_key = networks.jax.random.PRNGKey
    monkeypatch.setattr(networks.jax.random, "PRNGKey",
                        lambda value: (recorded.append(int(value)), real_key(value))[1])
    kwargs = dict(width=4, epochs=2, input_noise=0.1, batch_size=8)
    first = networks.train_mlp(inputs, targets, rng=make_rng(seed, "lorenz63", 7, 5, "estimator",
                                                             "0.01", 32), **kwargs)
    ref = hand()
    keys = [int(ref.integers(0, 2**32)) for _ in range(2)]
    assert recorded == keys

    n_val = max(1, int(0.1 * len(inputs)))
    order = ref.permutation(len(inputs))
    val = order[:n_val]
    noisy = inputs[val] + 0.1 * ref.standard_normal(inputs[val].shape)
    residual = np.asarray(first.predict(noisy)) - targets[val]
    assert first.val_loss == pytest.approx(float(np.mean(np.sum(residual**2, axis=1))),
                                           rel=1e-12, abs=0)

    second = networks.train_mlp(inputs, targets, rng=hand(), **kwargs)
    assert second.val_loss == first.val_loss
    for (w1, b1), (w2, b2) in zip(first.params, second.params):
        assert np.array_equal(np.asarray(w1), np.asarray(w2))
        assert np.array_equal(np.asarray(b1), np.asarray(b2))

    other = networks.train_mlp(inputs, targets, rng=make_rng(seed, "lorenz63", 7, 5, "estimator",
                                                             "0.01", 64), **kwargs)
    assert not np.array_equal(np.asarray(other.params[0][0]), np.asarray(first.params[0][0]))


def test_train_estimator_gives_each_width_its_own_fresh_stream(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """P7: ``train_estimator`` calls ``stream(width)`` once per width and trains from that stream.

    Reference: hand-built stubs. ``train_mlp`` is replaced by a recorder returning a stub network
    whose ``val_loss`` is 1.0 for both widths; the generators it receives must be in their initial
    state, equal to fresh generators for their own width and different between widths. The capacity
    rule (smallest width within 5% of the best) then keeps width 32 (equal losses, the smaller
    wins). Tolerance: none.
    """
    from lpcstudy import networks
    from lpcstudy.data import make_rng

    seen: dict[int, np.random.Generator] = {}

    def stub(inputs, targets, width, epochs, rng, input_noise=0.0, **kwargs):
        seen[width] = rng
        return SimpleNamespace(val_loss=1.0, width=width)

    monkeypatch.setattr(networks, "train_mlp", stub)
    stream = lambda width: make_rng(20261005, "rossler", 7, 8, "estimator", "0.02", width)
    net, losses = networks.train_estimator(np.zeros((4, 2)), np.zeros((4, 1)), 0.02, (32, 64), 1,
                                           stream)
    assert set(seen) == {32, 64} and net.width == 32 and losses == {32: 1.0, 64: 1.0}
    for width, rng in seen.items():
        assert rng.bit_generator.state == stream(width).bit_generator.state
    assert seen[32].bit_generator.state != seen[64].bit_generator.state
