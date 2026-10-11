"""Tests for lpcstudy.experiments: the sweep-cell restriction (WU-0002.7)."""

from __future__ import annotations

import dataclasses

import numpy as np

from lpcstudy.config import SMOKE
from lpcstudy.ensemble import EvaluationDraws
from lpcstudy.experiments import _sweep_subset
from lpcstudy.pipeline import Cell, SplitData
from unit_helpers import _moments_from_draws


class _Oracles:
    """Stand-in for ``StateOracles``: only ``subset`` is used by ``_sweep_subset``."""

    def subset(self, rows: np.ndarray) -> "_Oracles":
        return self


def test_sweep_subset_slices_the_correlation_fields_to_the_evaluation_horizons() -> None:
    """``_sweep_subset`` restricts ``err_corr``, ``cp_constant`` and ``plp_constant`` like the rest.

    Reference: direct indexing of the hand-built full-horizon arrays (entries are their own
    flat index, so the expected block is ``full[:n_sweep][:, eval_horizons - 1]``). The
    evaluation horizons of ``SMOKE`` are (8, 15, 30, 60, 120) steps; H_ref = 30 is the third
    column, and after slicing the column of H_ref equals the original column 29 of the first
    ``n_test_sweep`` rows (the plan's E2 check). The unsliced mean fields must change the same
    way. A cell without the fields stays without them (``None``). Exact (indexing only).
    """
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    n_states, n_draws, n_hor = 6, 3, 120
    rng = np.random.default_rng(9)
    moments = _moments_from_draws(rng.standard_normal((n_states, n_draws, n_hor)),
                                  rng.standard_normal((n_states, n_draws, n_hor)))
    grid = np.arange(n_states * n_hor, dtype=float).reshape(n_states, n_hor)
    moments = dataclasses.replace(moments, err_corr=grid, cp_constant=grid % 7 == 0,
                                  plp_constant=grid % 5 == 0)
    zeros = np.zeros((n_states, 2, n_hor))
    evals = EvaluationDraws(
        horizons=moments.horizons, cp_err=zeros, plp_err=zeros, verify_noise=zeros,
        distance=np.zeros((n_states, 2)), est_nu=np.zeros((n_states, 2)),
        growth_proxy=np.zeros((n_states, 2)), gain_proxy=zeros,
        inputs=np.zeros((n_states, 2, 1)), noise_sens=np.zeros((n_states, 2)))

    def cell_of(mom) -> Cell:
        return Cell(system="lorenz63", noise=0.01, library_size=10_000, label="base", setup=None,
                    splits={"test": SplitData(mom, evals)}, oracles={"test": _Oracles()},
                    horizons=np.arange(1, n_hor + 1))

    out = _sweep_subset(cell_of(moments), config).splits["test"].moments
    cols = np.array(config.eval_horizons) - 1
    np.testing.assert_array_equal(out.horizons, config.eval_horizons)
    np.testing.assert_array_equal(out.err_corr, grid[:4][:, cols])
    np.testing.assert_array_equal(out.cp_constant, (grid % 7 == 0)[:4][:, cols])
    np.testing.assert_array_equal(out.plp_constant, (grid % 5 == 0)[:4][:, cols])
    ref = out.at(config.reference_horizon)
    assert ref == 2
    np.testing.assert_array_equal(out.err_corr[:, ref], grid[:4, config.reference_horizon - 1])
    np.testing.assert_array_equal(out.mean_cp, moments.mean_cp[:4][:, cols])

    plain = _sweep_subset(cell_of(_moments_from_draws(
        rng.standard_normal((n_states, n_draws, n_hor)),
        rng.standard_normal((n_states, n_draws, n_hor)))), config).splits["test"].moments
    assert plain.err_corr is None and plain.cp_constant is None and plain.plp_constant is None
