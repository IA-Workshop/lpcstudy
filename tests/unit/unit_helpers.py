"""Shared helper for the unit tests (WU-0010.2)."""

from __future__ import annotations

import numpy as np

from lpcstudy.ensemble import EnsembleMoments


def _moments_from_draws(cp: np.ndarray, plp: np.ndarray) -> EnsembleMoments:
    return EnsembleMoments(
        horizons=np.arange(1, cp.shape[-1] + 1), mean_cp=cp.mean(1), mean_plp=plp.mean(1),
        sq_cp=(cp**2).mean(1), sq_plp=(plp**2).mean(1), cross=(cp * plp).mean(1),
        analog_seed=np.ones(len(cp)), est_seed=np.ones(len(cp)), noise_sens=np.zeros(len(cp)))
