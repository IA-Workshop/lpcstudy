"""Monte Carlo checks of ``tools/rehearsal_diagnostics.py`` (WU-0003.8, plan B2 row .8, c-slow).

DEVELOPMENT, synthetic data, fixed seeds through ``make_rng`` (master seed ``SEED``); needs owner
review before freeze (statistics feeding the block-length and M decisions). Slow tier, CPU, run once
by the .8 developer, who owns the statistic. Three checks; each states its reference, its Monte
Carlo (MC) error and why the bound was fixed before the run.

**S1. E V*(10)/V*(5) at phi = 0, n = 500.** Reference: ``m4_ratios.log`` of the mathematics check,
mean 0.987, SD 0.083 per series (R = 4000). Here R = 2000 iid Gaussian series; the MC SE of the mean
is 0.083/sqrt(2000) = 0.00186, so the bound is 0.987 +- 4 x 0.00186 = +- 0.0074 (the plan's text).

**S2. Trigger rate of the pooled permutation reading on iid data.** Reference: a permutation test at
the 0.99 quantile of 1000 permutations has size 0.01 under exchangeability; with the observed value
not among the null draws the size is 0.01 up to the quantile's own error. R = 500 systems of three
iid series (lengths 500, 500 and 300: the induced-order rule is exercised). The bound is the plan's:
rate <= 0.01 + 3 sqrt(0.0099/500) = 0.0233 (MC SE of a rate of 0.01 at R = 500 is 0.0045).

**S3. The attenuation A of D4 against a known A0.** Design (fixed before the run): n = 4000 states,
logit w ~ N(0, 0.18^2) (w in about (0.36, 0.64): every state delta-valid), the two half-draw optima
``u_A = w + e_A``, ``u_B = w + e_B`` with e ~ N(0, 0.02^2/2), so the 200-draw optimum is
``(u_A + u_B)/2`` with noise SD exactly 0.01 (the SD of a half is 0.01 sqrt 2); five independent N(0, 1) controls and an N(0, 1)
Lambda. The known value is the delta-method reliability of the logit of the 200-draw weight,
``A0^2 = Var(l)/(Var(l) + E v)`` with ``E v = E[sigma_200^2/(w (1 - w))^2]`` integrated by 80-point
Gauss-Hermite quadrature over l (the true w, not the noisy one): about 0.9755 (share of noise 0.049),
independent of the estimator. The tool's plug-in has three known finite-sample biases, all
well below the MC error here: (i) the ``w`` in ``v`` is the noisy one, a second-order relative bias
of ``8 sigma_200^2 = 8e-4`` in ``v`` (A: 2e-5); (ii) the residual variance of ``y~`` loses the
6 degrees of freedom of the intercept and five controls, ``(1 - 6/n)``, so the noise share is
overstated by 0.15% (A: -4e-5; at the pilot's ~330 interior states it is 1.8% of the share, a
stricter reading, noted in the unit Log); (iii) the ratio of two sample moments (1e-5). Their sum
is about 6e-5 against an MC SE of SD(A)/sqrt(R) = 5e-5 at R = 200, so the bound
``|mean(A) - A0| <= 4 SE`` has a margin of about 3. No bound was changed after a result was seen
(PRIME.2).
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
_SPEC = importlib.util.spec_from_file_location("rehearsal_diagnostics",
                                               ROOT / "tools" / "rehearsal_diagnostics.py")
assert _SPEC is not None and _SPEC.loader is not None
rd = importlib.util.module_from_spec(_SPEC)
sys.modules["rehearsal_diagnostics"] = rd
_SPEC.loader.exec_module(rd)

SEED = 20261031


def test_s1_variance_ratio_mean_at_phi_zero_matches_the_m4_log() -> None:
    """E V*(10)/V*(5) = 0.987 +- 4 x 0.083/sqrt(2000) for iid series of n = 500 (R = 2000)."""
    rng = make_rng(SEED, "mc", "s1")
    ratios = np.array([rd.variance_summary(rng.standard_normal(500))["ratio10"]
                       for _ in range(2000)])
    se = 0.083 / math.sqrt(2000)
    assert abs(ratios.mean() - 0.987) <= 4 * se, (ratios.mean(), ratios.std())


def test_s2_permutation_reading_has_size_at_most_the_plan_bound_on_iid_data() -> None:
    """The pooled permutation reading fires on at most 0.01 + 3 sqrt(0.0099/500) of 500 iid systems."""
    rng = make_rng(SEED, "mc", "s2")
    fires = 0
    for rep in range(500):
        series = [rng.standard_normal(500), rng.standard_normal(500), rng.standard_normal(300)]
        obs, null = rd.permutation_null(series, 1000, make_rng(SEED, "mc", "s2-keys", rep))
        fires += obs > np.quantile(null, 0.99)
    rate = fires / 500
    assert rate <= 0.01 + 3 * math.sqrt(0.0099 / 500), rate


def test_s3_attenuation_matches_the_known_delta_method_value_within_four_mc_se() -> None:
    """|mean A - A0| <= 4 SE over R = 200 replications of n = 4000 states (design in the docstring)."""
    n, reps, sd_l, sigma_h = 4000, 200, 0.18, 0.01 * math.sqrt(2.0)  # SD of one half-draw optimum
    nodes, weights = np.polynomial.hermite_e.hermegauss(80)
    w_true = 1.0 / (1.0 + np.exp(-sd_l * nodes))
    e_v = float(np.sum(weights * (sigma_h**2 / 2) / (w_true * (1 - w_true)) ** 2) / np.sum(weights))
    a0 = math.sqrt(sd_l**2 / (sd_l**2 + e_v))
    rng = make_rng(SEED, "mc", "s3")
    values = []
    for _ in range(reps):
        w = 1.0 / (1.0 + np.exp(-sd_l * rng.standard_normal(n)))
        u_a, u_b = w + sigma_h * rng.standard_normal(n), w + sigma_h * rng.standard_normal(n)
        out = rd.interior_attenuation(u_a, u_b, (u_a + u_b) / 2, rng.standard_normal((n, 5)),
                                      rng.standard_normal(n))
        assert out["n_excluded_delta"] == 0 and out["A"] is not None
        values.append(out["A"])
    values = np.array(values)
    se = values.std(ddof=1) / math.sqrt(reps)
    assert abs(values.mean() - a0) <= 4 * se, (values.mean(), a0, se)
