"""Null rate of the profile ablation for conditions that carry no information.

WU-0039b (ROADMAP WU-0039): "on a synthetic target that depends on known
conditions, the irrelevant conditions stay within the WU-0006.3 null rate". The
production function ``lpcstudy.ablation.profile_ablation_block`` is run on a
design in which the targets depend on R and O only, and I and N are
independent noise. An irrelevant condition is read "distinct" (or
"substantial") when the lower bound of its 95% interval is above 0; that must
not happen more often than the WU-0006.3 N2 bound allows.

**Design** (the WU-0006.3 null design of ``tests/slow/wu0006_harness.py``,
with the roles changed). x1, x2, x3, x4, e, e' are independent stationary
AR(1) with lag-1 phi = 0.3 (``wu.ar1``); the profile is (R, O, I, N) = (x1,
x2, x3, x4). L = x1 - 0.5 x2^2 + 0.5 x1 x2 + e; w* = 0 where L is below the
harness's threshold ``wu.DELTA_Q15`` (about 15% of states), else expit(L);
log horizon = 0.5 x1 + 0.3 x2 + 0.5 e'. All three targets depend on x1 and x2
and on noise independent of x3 and x4, so the population leave-one-out gain and
the population Shapley share of I and of N are 0 for every target. phi = 0.3
is the dependent case of WU-0006.3, where the block bootstrap must account for
the serial correlation. Sizes are the harness's (the full preset): 2000 + 1000
training states on two independent paths, one test path of 1000, 2000
resamples of blocks of 5, level 95%.

**Bound** (WU-0006.3 N2, the same rule at the same R): a false "distinct" has
nominal probability 0.025 (one tail of a 95% interval); over R = 500
replications the count must be at most ``floor(500 (0.025 + 3 sqrt(0.025 x
0.975 / 500))) = 22``, the N2 bound of 22 of 500 (0.045946). There are 12
counts: {I, N} x {logit w* interior, 1{w* = 0}, log horizon} x {leave-one-out,
Shapley}. WU-0006.3 measured the false-distinct rate of Q-N's gain at 0.009 to
0.019 (the learner pays for an irrelevant feature, so the conditional gain has
a negative mean); at a rate of 0.02 one count exceeds 22 with probability
about 3e-5, and at the nominal 0.025 about 0.002, so about 0.024 for the
family of 12 in the worst case. Monte Carlo error of a rate: sqrt(p (1 - p) /
500) = 0.007 at p = 0.025.

**Design check** (not a criterion): the relevant conditions must be detected,
or the null rate would be vacuous. R and O carry all the explainable variance
of every target (Var L = 2.75; dropping x1 removes the x1 and x1 x2 terms,
45% of it, and dropping x2 the x2^2 and x1 x2 terms, 27%), so their
leave-one-out lower bound must be above
0 in at least half of the replications. The bound is loose on purpose: a miss
means the design is too weak (a test defect), not a code defect.

Slow tier: about 4.5 s per replication on one thread (measured for the profile
block at these sizes), 500 replications on ``wu.pool_size()`` workers (at most
4): about 10 minutes. Counts are written to
``runs/tests/wu0039b_null_rate.json``.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pytest
from scipy.special import expit

import wu0006_harness as wu
from lpcstudy.ablation import CONDITIONS, profile_ablation_block
from lpcstudy.config import FULL
from lpcstudy.data import make_rng

PHI = 0.3
REPLICATIONS = 500
NOMINAL_RATE = 0.025
BOUND = math.floor(
    REPLICATIONS
    * (NOMINAL_RATE + 3 * math.sqrt(NOMINAL_RATE * 0.975 / REPLICATIONS))
)
TARGETS = ("logit_w_interior", "w_zero_indicator", "log_horizon")
ROWS = ("leave_one_out", "shapley")
IRRELEVANT = ("I", "N")
RELEVANT = ("R", "O")
SEED = 39030
CHUNK = 25


def null_states(
    rng: np.random.Generator, n: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Profile ``(n, 4)``, oracle weight and log horizon of the design."""
    x1, x2, x3, x4, e, e2 = (wu.ar1(rng, n, PHI) for _ in range(6))
    latent = x1 - 0.5 * x2**2 + 0.5 * x1 * x2 + e
    weight = np.where(latent < wu.DELTA_Q15, 0.0, expit(latent))
    profile = np.column_stack([x1, x2, x3, x4])
    return profile, weight, 0.5 * x1 + 0.3 * x2 + 0.5 * e2


def replicate(r: int) -> dict[str, float]:
    """One replication: 1.0 where a lower bound is above 0, per row."""
    key = (SEED, "wu0039b", "null-rate", f"{PHI:g}", r)
    rng, seed_rng = make_rng(*key, "data"), make_rng(*key, "boot")
    xa, wa, ta = null_states(rng, FULL.n_construction)
    xb, wb, tb = null_states(rng, FULL.n_calibration)
    x_test, w_test, t_test = null_states(rng, FULL.n_test)
    model_seed = int(seed_rng.integers(2**31))
    boot_seed = int(seed_rng.integers(2**31))
    out = profile_ablation_block(
        np.concatenate([xa, xb]),
        x_test,
        np.concatenate([wa, wb]),
        w_test,
        np.concatenate([ta, tb]),
        t_test,
        seed=model_seed,
        n_resamples=FULL.bootstrap_resamples,
        block=FULL.bootstrap_block,
        boot_seed=boot_seed,
    )
    found = {}
    for target in TARGETS:
        for row in ROWS:
            for x in CONDITIONS:
                lower = out[target][row][x]["ci"][0]
                found[f"{target}|{row}|{x}"] = float(lower > 0.0)
        gap = out[target]["shapley_sum"] - out[target]["r2_full_minus_empty"]
        found[f"{target}|shapley_gap"] = abs(gap)
    return found


def _task(bounds: tuple[int, int]) -> list[dict[str, float]]:
    """A chunk of replications (the unit of work of a worker)."""
    return [replicate(r) for r in range(*bounds)]


@pytest.fixture(scope="module")
def counts() -> dict[str, float]:
    """Run the replications once and sum them; write the table."""
    wu.assert_design()
    tasks = [
        (start, min(start + CHUNK, REPLICATIONS))
        for start in range(0, REPLICATIONS, CHUNK)
    ]
    with wu.worker_pool() as pool:
        rows = [r for chunk in wu.run_tasks(pool, _task, tasks) for r in chunk]
    assert len(rows) == REPLICATIONS
    total = {
        k: float(sum(r[k] for r in rows))
        for k in rows[0]
        if not k.endswith("gap")
    }
    total["max_shapley_gap"] = max(
        v for r in rows for k, v in r.items() if k.endswith("gap")
    )
    wu.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (wu.RESULTS_DIR / "wu0039b_null_rate.json").write_text(
        json.dumps(
            {"replications": REPLICATIONS, "bound": BOUND, "counts": total},
            indent=1,
        )
    )
    return total


def test_bound_is_the_wu0006_n2_bound() -> None:
    """The bound is N2's: 22 of 500 (0.025 + 3 SE at R = 500)."""
    assert BOUND == 22


@pytest.mark.parametrize("row", ROWS)
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("condition", IRRELEVANT)
def test_irrelevant_condition_stays_within_the_null_rate(
    counts: dict[str, float], condition: str, target: str, row: str
) -> None:
    """False "distinct" readings of I and N: at most 22 of 500 (N2 bound)."""
    found = counts[f"{target}|{row}|{condition}"]
    assert found <= BOUND, (condition, target, row, found)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("condition", RELEVANT)
def test_relevant_condition_is_detected(
    counts: dict[str, float], condition: str, target: str
) -> None:
    """Design check: the leave-one-out row of R and O is detected (>= 50%)."""
    found = counts[f"{target}|leave_one_out|{condition}"]
    assert found >= REPLICATIONS / 2, (condition, target, found)


def test_shapley_shares_sum_in_every_replication(
    counts: dict[str, float],
) -> None:
    """Efficiency holds in every replication within 1e-12 (round-off)."""
    assert counts["max_shapley_gap"] <= 1e-12
