"""Monte Carlo test of the kappa_E estimator of ``tools/rehearsal_report.py`` (WU-0003.3a, f2).

DEVELOPMENT. f2 of plan amendment 5: on synthetic data with known ``V_s`` and ``V_d``, the point
estimate ``kappa-hat_E`` (the estimator that the tool applies to a dump) lies within 4 Monte Carlo
standard errors of the truth. Fixed seed from ``make_rng``; the bounds below were fixed before any
run and are never changed to pass.

Design (independent states, so that the long-run variance is the plain variance):

* Difference criterion (H2c): the draw-free MSEs of the two rules are ``mu + s_s z`` with
  independent standard normals ``z``; the realized MSEs add independent draw noise ``s_d z'``
  (the noise at the run's ``E = 2`` evaluation draws). The influence of the mean difference is the
  centred difference, so ``V_s = 2 s_s^2`` and ``V_d = 2 s_d^2`` exactly, and
  ``kappa^2 = (V_s + V_d/2)/(V_s + V_d)`` (E 2 to 4, the draw variance halves).
* Ratio criterion (H2d, H3c): means ``mu_a, mu_b`` much larger than the spreads, so that to first
  order the influence is ``(a_i - R b_i)/mu_b`` with ``R = mu_a/mu_b``; ``V_s = (1 + R^2) s_s^2/mu_b^2``,
  ``V_d = (1 + R^2) s_d^2/mu_b^2`` and the same ``kappa`` formula. The estimator's O(1/n) finite-sample
  bias (n = 500) is at most 0.3% of the variances, and the two variances are biased alike, so the
  bias of kappa-hat is below 1e-3, under the 4 SE bound used here.

Tolerance: ``|mean(kappa-hat) - kappa| <= 4 SE``, ``SE = sd(kappa-hat)/sqrt(R)``, R = 2000
replications of n = 500 states. Monte Carlo error of the mean: the SD of kappa-hat is between
0.005 and 0.02 (relative SD of each variance estimate about sqrt(2/n) = 6%, damped by the derivative
of kappa^2 in the variance ratio t = V_d/V_s: -1/(2 (1 + t)^2), 1/8 at t = 1 and 1/50 at t = 4), so
SE is 1e-4 to 5e-4 and the bound 4e-4 to 2e-3. The probability that a correct, unbiased estimator
breaks the bound is 6e-5 per case. The test takes a few seconds (CPU).
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
_SPEC = importlib.util.spec_from_file_location("rehearsal_report",
                                               ROOT / "tools" / "rehearsal_report.py")
assert _SPEC is not None and _SPEC.loader is not None
rr = importlib.util.module_from_spec(_SPEC)
sys.modules["rehearsal_report"] = rr
_SPEC.loader.exec_module(rr)

SEED = 20261032
REPLICATIONS = 2000
STATES = 500


def replicate(kind: str, s_state: float, s_draw: float, label: str) -> np.ndarray:
    """``REPLICATIONS`` values of kappa-hat on independent synthetic worlds."""
    g = make_rng(SEED, "test_rehearsal_report_mc", label)
    mu_a, mu_b = (0.0, 0.0) if kind == "diff" else (30.0, 20.0)
    out = np.empty(REPLICATIONS)
    for r in range(REPLICATIONS):
        state_a = mu_a + s_state * g.standard_normal(STATES)
        state_b = mu_b + s_state * g.standard_normal(STATES)
        real_a = state_a + s_draw * g.standard_normal(STATES)
        real_b = state_b + s_draw * g.standard_normal(STATES)
        out[r] = rr.kappa_estimate(state_a, state_b, real_a, real_b, kind, 2, 4, block=5)[0]
    return out


def truth(kind: str, s_state: float, s_draw: float) -> float:
    """kappa from the exact ``V_s`` and ``V_d`` of the design."""
    weight = 2.0 if kind == "diff" else 1.0 + (30.0 / 20.0) ** 2
    scale = 1.0 if kind == "diff" else 1.0 / 20.0**2
    v_s, v_d = weight * s_state**2 * scale, weight * s_draw**2 * scale
    return math.sqrt((v_s + v_d * 2 / 4) / (v_s + v_d))


@pytest.mark.slow
@pytest.mark.parametrize(("kind", "s_state", "s_draw"), [("diff", 1.0, 1.0), ("diff", 1.0, 2.0),
                                                         ("ratio", 1.0, 1.0), ("ratio", 1.0, 2.0)])
def test_kappa_hat_is_within_four_standard_errors_of_the_truth(kind, s_state, s_draw) -> None:
    """f2: |mean kappa-hat - kappa| <= 4 SE, for kappa = 0.866, 0.775 (both designs)."""
    values = replicate(kind, s_state, s_draw, f"{kind}-{s_draw}")
    want = truth(kind, s_state, s_draw)
    se = float(values.std(ddof=1)) / math.sqrt(REPLICATIONS)
    assert se > 0.0
    assert abs(float(values.mean()) - want) <= 4.0 * se, (float(values.mean()), want, se)
