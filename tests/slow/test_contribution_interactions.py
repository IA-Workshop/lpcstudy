"""WU-0048 test (c): the B pair statistic on synthetic targets (slow tier).

The B procedure of lpcstudy.contribution (pair_jobs, run_job with
the production learner, state_loss, pair_rows) is run on a synthetic
regression target with four inputs, once additive and once with a planted
R x I term. Criterion (math spec, WU-0048 (c), as restated by addendum
R1 of WU-0045b): under the additive truth every pair has Holm-adjusted p >
0.05 (one-sided: no pair detected); with the planted term that pair is
detected (Holm p <= 0.05) and no other pair is.

The null criterion was restated by its owner, the applied-mathematician,
because the original was self-contradictory: it also asked for every upper
bound of Delta to be >= 0, while stating that under an additive truth the
fixed-model gain is <= 0 in expectation (the pair model can only overfit).
With 1000 fixed-model test states the overfitting penalty can be resolved,
and for R x O it was (Delta -0.0110 [-0.0212, -0.0016]); that clause controls
no error rate. Such a row reads "no interaction gain; the pair model fits
worse", which this test also checks.
Sizes and seeds are fixed below. Slow because every one of the 14 models is
selected by five-fold CV over three settings (about 200 fits). Each test is a
single fixed-seed check, not a rate: no Monte Carlo error applies.
"""

from __future__ import annotations

import numpy as np
import pytest

from lpcstudy import contribution as cb

pytestmark = pytest.mark.slow


def _pair_experiment(planted: float) -> dict:
    """Fit the B variants on a synthetic target; return ``pair_rows``.

    Sizes and seeds are fixed: 2000 training and 1000 test states, four
    standard normal inputs, additive part ``sin(x0) + x1^2 / 2 + 0.5 x2 +
    0.3 x3``, noise SD 0.5, plus ``planted x0 x2`` (an R x I term); 500
    moving-block resamples (block 5). The production learner: inner blocked
    CV over GRID for every model, as B uses it.
    """
    rng = np.random.default_rng(48005)
    n_train, n_test = 2000, 1000
    x = rng.standard_normal((n_train + n_test, 4))
    y = (
        np.sin(x[:, 0])
        + 0.5 * x[:, 1] ** 2
        + 0.5 * x[:, 2]
        + 0.3 * x[:, 3]
        + planted * x[:, 0] * x[:, 2]
        + 0.5 * rng.standard_normal(n_train + n_test)
    )
    train, test = slice(0, n_train), slice(n_train, None)
    base = cb.FitJob(
        "regression",
        x[train, None, :],
        y[train],
        None,
        np.ones(n_train, bool),
        np.arange(n_train),
        x[test, None, :],
        "squared",
        {"y": y[train]},
    )
    learner = cb.Learner(seed=11)
    jobs = cb.pair_jobs(base, full=False)
    results = {k: cb.run_job((job, learner)) for k, job in jobs.items()}
    losses = {
        k: cb.state_loss("squared", r.pred, {"y": y[test]})
        for k, r in results.items()
    }
    index = cb.resample_indices(n_test, 500, 5, np.random.default_rng(48006))
    return cb.pair_rows(losses, index)


def test_c_additive_target_has_no_detected_pair() -> None:
    """(c), null: every pair has Holm-adjusted p > 0.05 (addendum R1).

    Reference: the data are additive by construction. Tolerance: Holm at 5%
    on one-sided bootstrap p-values (family-wise false detection <= 0.05,
    approximately; conservative when E[Delta] < 0), so this fixed-seed check
    fails spuriously with probability <= 0.05. A row whose upper bound is
    below 0 must read "no interaction gain; the pair model fits worse".
    """
    rows = _pair_experiment(0.0)["pairs"]
    for name, row in rows.items():
        assert row["p_holm"] > 0.05, (name, row)
        assert not row["detected"], (name, row)
        if row["ci"][1] < 0.0:
            assert row["reading"] == cb.NO_GAIN, (name, row)


def test_c_planted_r_by_i_term_is_detected_and_no_other_pair() -> None:
    """(c), planted: ``R x I`` (``x0 x2``, coefficient 1) is detected (Holm p
    <= 0.05) and no other pair is.

    Reference: the planted term. Tolerance: Holm at 5%.
    """
    rows = _pair_experiment(1.0)["pairs"]
    assert rows["RI"]["detected"], rows["RI"]
    assert rows["RI"]["primary"]
    for name, row in rows.items():
        if name != "RI":
            assert not row["detected"], (name, row)
