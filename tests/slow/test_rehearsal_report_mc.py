"""Monte Carlo test of the kappa_E estimator of ``tools/rehearsal_report.py`` (WU-0003.3a, f2).

The rehearsal report projects how wide the study's confidence intervals will be at
other sample sizes. The factor kappa_E measures how much of the variance comes from
the finite number of evaluation draws (E) instead of from the differences between
states, so it tells how the width changes if E changes (here from 2 to 4). The test
makes synthetic data in which the two variances, V_s (between states) and V_d (from
draws), are known exactly, so the true kappa is known, and checks that the tool's
estimate averages to it over many repetitions (a "Monte Carlo" experiment).

DEVELOPMENT. f2 of plan amendment 5: on synthetic data with known ``V_s`` and ``V_d``, the point
estimate ``kappa-hat_E`` (the estimator that the tool applies to a dump) lies within 4 Monte Carlo
standard errors of the truth. Fixed seed from ``make_rng``; the bounds below were fixed before any
run and are never changed to pass.

Design (independent states, so that the long-run variance is the plain variance):

* Difference criterion (H2c): the draw-free MSEs of the two rules are ``mu + s_s z`` with
  independent standard normals ``z``; the realized MSEs add independent draw noise ``s_d z'``
  (the noise at the run's ``E = 2`` evaluation draws). The influence of the mean difference is the
  centered difference, so ``V_s = 2 s_s^2`` and ``V_d = 2 s_d^2`` exactly, and
  ``kappa^2 = (V_s + V_d/2)/(V_s + V_d)`` (E 2 to 4, the draw variance halves).
* Ratio criterion (H2d, H3c): means ``mu_a, mu_b`` much larger than the spreads, so that to first
  order the influence is ``(a_i - R b_i)/mu_b`` with ``R = mu_a/mu_b``; ``V_s = (1 + R^2) s_s^2/mu_b^2``,
  ``V_d = (1 + R^2) s_d^2/mu_b^2`` and the same ``kappa`` formula.

Tolerance: ``|mean(kappa-hat) - kappa| <= 4 SE``, ``SE = sd(kappa-hat)/sqrt(R)``, R = 2000
replications of n = 500 states. Monte Carlo error: the SD of kappa-hat is 0.0085 to 0.012 (relative
SD of each variance estimate about sqrt(2/n) = 6%, damped by the derivative of kappa^2 in the
variance ratio t = V_d/V_s), so SE is 1.9e-4 to 2.7e-4 and the bound 7.6e-4 to 1.1e-3.

**The estimator is not exactly unbiased, and the margin is thin.** kappa is a nonlinear function of
the variance ratio, so kappa-hat has a second-order (Jensen) bias. At t = 4 (s_d = 2) the analytic
value is about +3.6e-4 and an independent simulation (R = 40000, the reviewer's) gives +3.9e-4 +- 0.4e-4
for the difference design and +2.9e-4 for the ratio design (0.05% of kappa; practically negligible, a
projected half-width moves by 0.05%). At R = 2000 that is 2.1 SE (1.5 SE for the ratio design), so with
this seed the difference design at s_d = 2 is recorded at +3.85 SE (about 2.1 SE of bias plus 1.8 SE of
seed noise). A correct estimator under another seed would break the bound in that case with
probability about 3% (about 1% for the ratio design at s_d = 2; at s_d = 1 the bias is below 6e-5 and
the probability is the 6e-5 of a 4 SE bound). The test is deterministic with its seed and passes, but
it is fragile under a change of R or seed (an R of about 8000 would put the bias at the bound). The
bound, the seed and R are fixed and must not be changed to pass; whether to compare with the truth
plus the predicted bias is a planner question. The test takes a few seconds (CPU).
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

from lpcstudy.data import make_rng

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "rehearsal_report", ROOT / "tools" / "rehearsal_report.py"
)
assert _SPEC is not None and _SPEC.loader is not None
rr = importlib.util.module_from_spec(_SPEC)
sys.modules["rehearsal_report"] = rr
_SPEC.loader.exec_module(rr)

SEED = 20261032
REPLICATIONS = 2000
STATES = 500


def replicate(
    kind: str, s_state: float, s_draw: float, label: str
) -> np.ndarray:
    """Return ``REPLICATIONS`` values of kappa-hat, each from an independent synthetic data set.

    ``kind`` is ``diff`` (difference criterion) or ``ratio`` (ratio criterion);
    ``s_state`` and ``s_draw`` are the between-state and draw noise sizes.
    """
    g = make_rng(SEED, "test_rehearsal_report_mc", label)
    mu_a, mu_b = (0.0, 0.0) if kind == "diff" else (30.0, 20.0)
    out = np.empty(REPLICATIONS)
    for r in range(REPLICATIONS):
        state_a = mu_a + s_state * g.standard_normal(STATES)
        state_b = mu_b + s_state * g.standard_normal(STATES)
        real_a = state_a + s_draw * g.standard_normal(STATES)
        real_b = state_b + s_draw * g.standard_normal(STATES)
        out[r] = rr.kappa_estimate(
            state_a, state_b, real_a, real_b, kind, 2, 4, block=5
        )[0]
    return out


def truth(kind: str, s_state: float, s_draw: float) -> float:
    """Return the true kappa, computed from the exact ``V_s`` and ``V_d`` of the design."""
    weight = 2.0 if kind == "diff" else 1.0 + (30.0 / 20.0) ** 2
    scale = 1.0 if kind == "diff" else 1.0 / 20.0**2
    v_s, v_d = weight * s_state**2 * scale, weight * s_draw**2 * scale
    return math.sqrt((v_s + v_d * 2 / 4) / (v_s + v_d))


@pytest.mark.slow
@pytest.mark.parametrize(
    ("kind", "s_state", "s_draw"),
    [
        ("diff", 1.0, 1.0),
        ("diff", 1.0, 2.0),
        ("ratio", 1.0, 1.0),
        ("ratio", 1.0, 2.0),
    ],
)
def test_kappa_hat_is_within_four_standard_errors_of_the_truth(
    kind, s_state, s_draw
) -> None:
    """f2: the mean of kappa-hat is within 4 standard errors of the true kappa.

    The true values are kappa = 0.866 and 0.775, for both designs.
    """
    values = replicate(kind, s_state, s_draw, f"{kind}-{s_draw}")
    want = truth(kind, s_state, s_draw)
    se = float(values.std(ddof=1)) / math.sqrt(REPLICATIONS)
    assert se > 0.0
    assert abs(float(values.mean()) - want) <= 4.0 * se, (
        float(values.mean()),
        want,
        se,
    )
