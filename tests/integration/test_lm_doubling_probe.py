"""The Part A capture of ``tools/lm_doubling.py`` against the pipeline's own moments (WU-0005.6b, P0).

Reference: ``ensemble_moments``, the pipeline function that makes the stored ``lm`` summaries,
called with estimators built from scratch (``StateEstimator(...)``, not by ``derive_estimator``)
on the same trained network, library and oracle noise. The capture goes through ``forecast_draws``
in the same chunks, so every array that both produce must agree bit for bit (same compilation,
same batch shapes, same threads): the final cost, the accepted count, the late-progress flag, the
per-state second moments of the errors and the replacement counts. The one quantity computed
differently is the r.m.s. whitened seed (``sqrt(mean(serr^2))`` against ``sqrt(mean(sum of
squares))``), compared at 1e-12 relative: two orderings of at most 1 + 3 + 1 float operations,
about 5 unit round-offs, with a margin of 1e4. The chunk size is lowered to 40 trajectories so that
the 24 states x 7 draws are cut into five chunks (5, 5, 5, 5, 4 states) and the chunk logic is used.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from lpcstudy.config import SMOKE
from lpcstudy.ensemble import DRAW_COLUMN, AnalogLibrary, ensemble_moments
from lpcstudy.estimation import StateEstimator
from lpcstudy.pipeline import Study
from lpcstudy.seeds import REGISTRY_PATH, load_registry, resolve_dev_seed, with_seed

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("lm_doubling", ROOT / "tools" / "lm_doubling.py")
assert _SPEC is not None and _SPEC.loader is not None
lm = importlib.util.module_from_spec(_SPEC)
sys.modules["lm_doubling"] = lm
_SPEC.loader.exec_module(lm)

LEVELS = (15, 30)
N_STATES, N_DRAWS, CHUNK = 24, 7, 40


@pytest.fixture(scope="module")
def world(tmp_path_factory: pytest.TempPathFactory):
    """A smoke study of Lorenz-63 on the development seed DEV-0: context, network, library."""
    config = with_seed(SMOKE, "DEV-0", resolve_dev_seed("DEV-0", load_registry(REGISTRY_PATH)))
    study = Study(config, tmp_path_factory.mktemp("probe"))
    ctx = study.context("lorenz63")
    setup = study.setup(ctx, config.core_noise)
    library = AnalogLibrary.build(ctx, config.core_noise, config.core_library, config.horizon_max)
    return config, study, ctx, setup, library


def test_capture_segment_reproduces_ensemble_moments_bitwise(world) -> None:
    """The capture at 15 and 30 iterations equals ``ensemble_moments`` with fresh estimators.

    Also: the replacement flags have the shape of the draws, the segment is whitened, and the
    estimator of each level is a separate object that shares the network.
    """
    config, study, ctx, setup, library = world
    horizons = np.array([h for h in config.eval_horizons if h >= config.steps_per_lyapunov])
    spec = lm.Spec("c", "oracle", "test", config.core_noise, slice(0, N_STATES), N_DRAWS, True)
    estimators = {k: lm.derive_estimator(setup.estimator, k) for k in LEVELS}
    segment = lm.capture_segment(study, setup, library, spec, estimators, horizons,
                                 config.reference_horizon, chunk_traj=CHUNK)
    noise = study.unit_noise(ctx, "test", "oracle", N_DRAWS, ctx.embed_dim)[:N_STATES]
    assert [len(r) for r in lm.chunk_rows(N_STATES, N_DRAWS, CHUNK)] == [5, 5, 5, 5, 4]
    for level in LEVELS:
        fresh = StateEstimator(ctx=ctx, network=setup.estimator.network,
                               model_step=setup.model_step, refine_steps=level)
        moments = ensemble_moments(dataclasses.replace(setup, estimator=fresh), library, "test",
                                   noise, horizons, chunk_traj=CHUNK,
                                   reference_horizon=config.reference_horizon)
        assert estimators[level].network is setup.estimator.network
        assert segment.c[level].tobytes() == moments.lm_residual.tobytes()
        assert segment.accepted[level].tobytes() == moments.lm_accepted.tobytes()
        assert segment.late[level].tobytes() == moments.lm_late.tobytes()
        assert segment.sq_plp[level].tobytes() == moments.sq_plp.tobytes()
        assert segment.cross[level].tobytes() == moments.cross.tobytes()
        assert segment.cp_sq.tobytes() == moments.sq_cp.tobytes()
        for name in lm.LM_COUNTS:
            assert segment.counts[level][name] == int(moments.handled[:, DRAW_COLUMN[name]].sum())
        rms_seed = np.sqrt((segment.serr[level] ** 2).mean(axis=1))
        assert rms_seed == pytest.approx(moments.est_seed, rel=1e-12)
        assert segment.replaced[level].shape == (N_STATES, N_DRAWS)
        assert segment.s[level].shape == (N_STATES, N_DRAWS, 3)
    assert np.all(segment.c[30] <= segment.c[15]) and np.all(segment.accepted[30] >= segment.accepted[15])


def test_pooled_summary_of_the_capture_is_the_pipelines_lm_summary(world) -> None:
    """Pooling two splits' segments gives the ``lm_summary`` the pipeline stores for their kind.

    Reference: ``pipeline.lm_block`` (the function that builds the stored block) on the moments of
    the same two splits made by ``ensemble_moments`` with fresh estimators. Exact (None = None).
    """
    from lpcstudy.estimation import lm_summary
    from lpcstudy.pipeline import lm_block
    config, study, ctx, setup, library = world
    horizons = np.array([30, 60, 120])
    segments, parts = [], []
    fresh = StateEstimator(ctx=ctx, network=setup.estimator.network, model_step=setup.model_step,
                           refine_steps=30)
    for split in ("calibration", "test"):
        spec = lm.Spec("c", "oracle", split, config.core_noise, slice(0, 10), N_DRAWS, True)
        segments.append(lm.capture_segment(
            study, setup, library, spec, {30: lm.derive_estimator(setup.estimator, 30)}, horizons,
            config.reference_horizon, chunk_traj=CHUNK))
        noise = study.unit_noise(ctx, split, "oracle", N_DRAWS, ctx.embed_dim)[:10]
        moments = ensemble_moments(dataclasses.replace(setup, estimator=fresh), library, split,
                                   noise, horizons, chunk_traj=CHUNK,
                                   reference_horizon=config.reference_horizon)
        parts.append((moments.lm_residual, moments.lm_accepted, moments.lm_late))
    stored = lm_block({"oracle": parts}, config.core_noise, ctx.embed_dim - ctx.spec.dim)
    summary, counts = lm.pooled_summary(segments, 30, lm_summary)
    assert summary == stored["by_kind"]["oracle"]
    assert lm.compare_p0(stored["by_kind"]["oracle"], counts, summary, counts) == []
