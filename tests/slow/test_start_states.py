"""Tests S-D1 and S-D2: are the seed-drawn start states of a run safe and well
distributed? (WU-0002.14).

Each study run starts its three chaotic systems (Lorenz-63, Rossler, Chua) from
states that are drawn from the run's seed by ``lpcstudy.data.draw_starts``. Two
things could go wrong. First, a start could make the trajectory blow up or leave
a sensible region, and then the run would be refused by the orbit guard
(``systems.guard_orbit``). Second, the starts could be concentrated in the wrong
part of the attractor (the set the system settles onto) instead of looking like
typical states. S-D1 checks safety by running 400 starts from 200 made-up seeds
for the full run length and counting refusals. S-D2 checks the distribution with
the Kolmogorov-Smirnov statistic, which is the largest gap between two
cumulative distribution curves, comparing the starts after the burn-in (the
initial stretch that is thrown away) with a long reference orbit. The helper
functions at the top advance a whole batch of starts at once.

DEVELOPMENT: synthetic seeds only (62-bit integers from
``numpy.random.default_rng(14002)``), never a registry seed and never the sealed
seed. Seed code: needs owner review before freeze. Slow tier: per system the
cost is the statistics orbit (203 000 steps), the Benettin exponent and two
vmapped scans of 400 starts for about 7.1e5 steps (a few seconds each on one CPU
core); run once, by the developer of the unit, with the results in the unit log.

What is checked (the plan and its mathematics check, M1 and M6; the numbers were
fixed there):

* **S-D1 safety.** For N = 200 synthetic seeds the 400 starts of a system (main
  and estimator), drawn by ``data.draw_starts`` on the production statistics
  orbit, are run for ``burn + 705 000`` steps (the burn-in plus the full-preset
  main length, which is longer than the estimator's) under the orbit guard of
  ``systems.guard_orbit`` (finite, ``|x| <= B``, the start included), vectorized
  over the starts. **0 refusals.** The rule of three alone gives only a 1.5%
  bound at 95%; the bound for a confirmatory seed comes from the mathematics
  check (M1(b)), not from this test. A **stress arm** repeats the same seeds at
  ``eta = 1e-3`` for the burn-in only: 0 refusals, through the real code path
  (whitening, eta and the guard), so a units or scaling error would show. A
  **negative control** (a start at twice the bound) must be refused by the same
  vectorized guard, so the check cannot pass vacuously.
* **S-D2 distribution.** The ``x`` of the 400 states after the burn-in (main and
  estimator pooled, independent draws) against the ``x`` marginal of the
  2e5-state statistics orbit: the two-sample Kolmogorov-Smirnov statistic is at
  most ``D_crit = c(0.001) sqrt(1/400 + 1/200000) = 1.94947 * 0.05013 = 0.0976``
  (alpha = 0.001 per system, family 0.003). The effective size of the
  autocorrelated reference is at least 7000 (M6), so the true level is at most
  1.5e-3. The statistic detects a start that stays near the registry state (D
  about 0.40 for Rossler); it cannot detect a missing burn-in (``stats[k] +
  eta`` is already distributed like the orbit), which is why the burn-in is
  pinned by P8 in the unit tier.

Tolerances: S-D1 counts (0 refusals), S-D2 the derived D_crit; neither is to be
changed to pass (PRIME.2).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest
from scipy import stats as sps

from lpcstudy.config import PILOT
from lpcstudy.data import (
    START_PERTURBATION,
    _symmetric_root,
    draw_starts,
    lyapunov_record,
)
from lpcstudy.systems import (
    SYSTEMS,
    checked_bound,
    make_flow_step,
    simulate_trajectory,
)

N_SEEDS = 200
SYNTHETIC_SEEDS = [
    int(v) for v in np.random.default_rng(14002).integers(0, 2**62, N_SEEDS)
]
# steps after the burn-in: the full-preset main length (7.05e5)
HORIZON = 705_000
STRESS_ETA = 1e-3
N_REFERENCE = 200_000
C_ALPHA_001 = 1.94947  # c(alpha) of the two-sample KS test at alpha = 0.001
D_CRIT = C_ALPHA_001 * math.sqrt(1.0 / (2 * N_SEEDS) + 1.0 / N_REFERENCE)
SUMMARY_PATH = (
    Path(__file__).resolve().parents[2] / "runs" / "tests" / "start_states.json"
)
SUMMARY: dict[str, dict] = {}


def _advance(step, state, largest, finite, n_steps: int):
    """Run ``n_steps`` of the flow map on a batch, tracking ``max |x_0|`` and
    finiteness.
    """
    batched = jax.vmap(step)

    def body(carry, _):
        current, big, ok = carry
        nxt = batched(current)
        ok = ok & jnp.all(jnp.isfinite(nxt), axis=1)
        big = jnp.maximum(
            big, jnp.abs(nxt[:, 0])
        )  # NaN propagates, so a NaN fails below
        return (nxt, big, ok), None

    (final, big, ok), _ = jax.jit(
        lambda c: jax.lax.scan(body, c, None, length=n_steps)
    )((state, largest, finite))
    return final, big, ok


def _start_batch(state: np.ndarray):
    """Pack start states into the ``(state, largest |x|, all finite)`` triple
    that ``_advance`` takes.
    """
    return (
        jnp.asarray(state, dtype=jnp.float64),
        jnp.abs(jnp.asarray(state[:, 0], jnp.float64)),
        jnp.all(jnp.isfinite(jnp.asarray(state, jnp.float64)), axis=1),
    )


def _refused(largest, finite, bound: float) -> np.ndarray:
    """Apply the rule of ``systems.guard_orbit`` to a batch.

    A start is refused if it is not finite, or if its largest ``|x|`` exceeds
    the bound ``B``.
    """
    return ~np.asarray(finite) | ~(np.asarray(largest) <= bound)


@pytest.fixture(scope="module", params=sorted(SYSTEMS))
def run(request, tmp_path_factory) -> dict:
    """Run the starts of one system and return everything S-D1 and S-D2 need.

    The module-scoped fixture runs once for each system in ``SYSTEMS``.
    """
    name = request.param
    spec = SYSTEMS[name]
    cfg = PILOT
    bound = checked_bound(spec)
    lam, _ = lyapunov_record(
        spec, tmp_path_factory.mktemp(name) / "lyapunov.json"
    )
    interval = 1.0 / (cfg.steps_per_lyapunov * lam)
    step = make_flow_step(spec, spec.params, interval)
    burn = int(cfg.burn_in_lyapunov * cfg.steps_per_lyapunov)
    orbit = simulate_trajectory(
        step, jnp.asarray(spec.initial_state), burn + N_REFERENCE
    )[burn:]
    _, unwhiten = _symmetric_root(np.cov(orbit.T))

    def starts(eta: float) -> np.ndarray:
        drawn = [
            draw_starts(seed, name, orbit, unwhiten, eta)
            for seed in SYNTHETIC_SEEDS
        ]
        return np.array(
            [s.main_state for s in drawn] + [s.estimator_state for s in drawn]
        )

    batch = starts(START_PERTURBATION)
    state, big, ok = _advance(step, *_start_batch(batch), burn)
    x_burn = np.asarray(state)[:, 0].copy()
    state, big, ok = _advance(step, state, big, ok, HORIZON)
    stress = starts(STRESS_ETA)
    _, stress_big, stress_ok = _advance(step, *_start_batch(stress), burn)
    # The control row has one entry per state coordinate (a hard-coded 3
    # failed for the 4-dimensional S1 of WU-0021; identical for dim 3).
    control = np.vstack(
        [batch[:3], [[2.0 * bound] + [0.0] * (orbit.shape[1] - 1)]]
    )
    _, control_big, control_ok = _advance(step, *_start_batch(control), 10)
    out = {
        "name": name,
        "bound": bound,
        "orbit": orbit,
        "x_burn": x_burn,
        "refused": _refused(big, ok, bound),
        "largest": np.asarray(big),
        "stress_refused": _refused(stress_big, stress_ok, bound),
        "stress_largest": np.asarray(stress_big),
        "control_refused": _refused(control_big, control_ok, bound),
        "starts": batch,
        "stress_starts": stress,
    }
    SUMMARY[name] = {
        "n_starts": int(len(batch)),
        "steps_per_start": int(burn + HORIZON),
        "refusals": int(out["refused"].sum()),
        "max_abs_x": float(out["largest"].max()),
        "stress_eta": STRESS_ETA,
        "stress_refusals": int(out["stress_refused"].sum()),
        "stress_max_abs_x": float(out["stress_largest"].max()),
        "bound": bound,
    }
    return out


def test_sd1_no_start_is_refused_over_the_full_horizon(
    run: dict, request: pytest.FixtureRequest
) -> None:
    """S-D1: 0 refusals for 400 starts over ``burn + 705 000`` steps; the
    control is refused.

    Reference: the rule of three (if 0 of 400 runs fail, the failure probability
    is below 3/400 = 0.75% at 95% confidence; 1.5% for the 200 seeds) and the
    bound B of the system. The control (a start at 2B) must be flagged, which
    shows that the vectorized guard works. Tolerance: none (a count).
    """
    assert len(run["starts"]) == 2 * N_SEEDS
    assert run["control_refused"].tolist() == [
        False,
        False,
        False,
        True,
    ], "the control is vacuous"
    if run["name"] == "rossler_hyper":
        # Pre-stated criterion S-D1 not met by S1 (WU-0021): measured 10 of 400
        # starts refused over burn + 705 000 steps, 7 of them non-finite. The
        # mechanism is under review (WU-0021 review R1: RK4 stability at the
        # production step and the bound). The owner's ruling keeps S1 and
        # reports a refusal as a result; the criterion is not loosened. The
        # start count and the control row are asserted above this branch, so a
        # broken guard still fails. The next two asserts are a regression
        # guard of the measured counts (this host and XLA build, the 400
        # synthetic starts of this module): any other count is a failure, not
        # an xfail. The xfail is strict: an unexpected pass is noticed.
        assert int(run["refused"].sum()) == 10, "S1 refusal count changed"
        assert int(np.isnan(run["largest"]).sum()) == 7, "S1 non-finite count"
        request.node.add_marker(
            pytest.mark.xfail(
                strict=True,
                reason="S-D1 not met by S1: 10 of 400 starts refused, 7 "
                "non-finite (WU-0021 Referral and review R1)",
            )
        )
    assert not run["refused"].any(), (
        f"{run['name']}: {int(run['refused'].sum())} of {len(run['refused'])} starts refused; "
        f"max|x| {run['largest'].max():.6g}, bound {run['bound']:g}"
    )
    assert run["largest"].max() <= run["bound"]


def test_sd1_stress_arm_at_eta_1e3_burn_in_only(run: dict) -> None:
    """S-D1 stress arm: the same seeds at eta = 1e-3, burn-in only, 0 refusals.

    Here eta is the size of the random offset added to a start. Reference: the
    escape table of the mathematics check (M1(b)): no escape at a whitened
    offset of 3e-3 or less on any system (Rossler's first escape is at 2e-2,
    Chua's at 0.2), and a margin of more than 10 against 1e-3. The offsets are
    drawn through the real ``draw_starts`` with the production whitening, so a
    units or scaling error would produce refusals. Tolerance: none.
    """
    assert not run["stress_refused"].any(), (
        f"{run['name']}: {int(run['stress_refused'].sum())} stress starts refused; "
        f"max|x| {run['stress_largest'].max():.6g}, bound {run['bound']:g}"
    )
    offsets = np.linalg.norm(run["stress_starts"] - run["starts"], axis=1)
    assert (
        1e-4 < offsets.max()
    )  # the stress arm differs from the base arm (not vacuous)


def test_sd2_the_x_marginal_after_the_burn_in_matches_the_statistics_orbit(
    run: dict,
) -> None:
    """S-D2: the KS distance of the pooled post-burn ``x`` (n = 400) to the
    orbit's ``x`` distribution.

    Reference: the two-sample Kolmogorov-Smirnov statistic of
    ``scipy.stats.ks_2samp`` against the 2e5 orbit states (an independent sample
    of the invariant measure, the long-run distribution of the system), and
    ``D_crit`` = 0.0976 (derived in the module docstring, fixed before the run).
    Recorded in ``runs/tests/start_states.json``. The test also computes the
    statistic for the starts BEFORE the burn-in, which equals the orbit's
    distribution by construction (``stats[k] + eta``), as a reminder that this
    test cannot see a missing burn-in. Tolerance: ``D <= 0.0976``.
    """
    reference = run["orbit"][:, 0]
    d_burned = float(sps.ks_2samp(run["x_burn"], reference).statistic)
    d_raw = float(sps.ks_2samp(run["starts"][:, 0], reference).statistic)
    SUMMARY[run["name"]].update(
        ks_d_after_burn_in=d_burned, ks_d_before_burn_in=d_raw, d_crit=D_CRIT
    )
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(SUMMARY, indent=1, sort_keys=True))
    assert (
        d_burned <= D_CRIT
    ), f"{run['name']}: D = {d_burned:.4f} > D_crit = {D_CRIT:.4f}"
