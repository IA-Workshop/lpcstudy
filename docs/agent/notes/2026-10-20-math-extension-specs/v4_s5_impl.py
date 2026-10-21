"""V4 of S5 on the implementation's real pipeline (PYTHONPATH = wu/ext-impl2;
DEVELOPMENT, one thread, no preset run): the convergence_check recipe on the
core cell with M up to 200 on 40 test states, per-state diagnostics, for (A)
the smoke configuration as run (3 epochs, 5 000 pairs, width 32) and (B) the
same with the pilot estimator settings (25 epochs, 40 000 pairs, width 64).
Reports the median bootstrap half-width of w*(H_ref) at M = 10, 30, 100, 200,
the per-state curvature c, w*, the fraction of PLP draws more than 1 sigma_x
in error at H_ref (wrong-basin estimates) and the CP/PLP constancy."""

import dataclasses
import tempfile
import time
from pathlib import Path

import numpy as np

from lpcstudy.config import SMOKE
from lpcstudy.data import make_rng
from lpcstudy.ensemble import AnalogLibrary, forecast_draws
from lpcstudy.pipeline import Study

SYSTEM = "hyper_jha"


def weight(c, p):
    num = np.mean(p * (p - c), axis=-1)
    den = np.mean((c - p) ** 2, axis=-1)
    return np.clip(num / np.maximum(den, 1e-300), 0, 1)


for label, cfg in (
    ("A smoke estimator", dataclasses.replace(SMOKE, convergence_draws=(10, 30, 100, 200), convergence_states=40)),
    ("B pilot estimator", dataclasses.replace(SMOKE, convergence_draws=(10, 30, 100, 200), convergence_states=40,
                                              estimator_epochs=25, estimator_pairs=40_000, estimator_widths=(64,))),
):
    t0 = time.time()
    study = Study(cfg, Path(tempfile.mkdtemp(prefix="v4s5-")))
    ctx = study.context(SYSTEM)
    cell = study.run_cell(SYSTEM, cfg.core_noise, cfg.core_library, core=True, with_evals=False)
    n = min(cfg.convergence_states, cfg.n_test)
    noise = study.unit_noise(ctx, "test", "convergence", 200, ctx.embed_dim)[:n]
    library = AnalogLibrary.build(ctx, cell.noise, cell.library_size, cfg.horizon_max)
    horizons = np.array([cfg.reference_horizon])
    cp, plp = [], []
    for start in range(0, n, 5):
        rows = np.arange(start, min(n, start + 5))
        batch = forecast_draws(cell.setup, library, "test", rows, noise[rows], horizons, cfg.reference_horizon)
        cp.append(batch.cp_err[:, :, 0]); plp.append(batch.plp_err[:, :, 0])
    cp, plp = np.concatenate(cp), np.concatenate(plp)
    rng = make_rng(cfg.seed, SYSTEM, "V4-convergence")
    print(f"[{label}] {SYSTEM}: estimator {study.estimator_log}; n states {n}; [{time.time()-t0:.0f} s]")
    halves = {}
    for m in cfg.convergence_draws:
        base = weight(cp[:, :m], plp[:, :m])
        idx = rng.integers(0, m, (200, m))
        boots = np.stack([weight(cp[:, i], plp[:, i]) for i in idx])
        half = 0.5 * (np.percentile(boots, 97.5, axis=0) - np.percentile(boots, 2.5, axis=0))
        halves[m] = half
        print(f"   M {m:4d}: median half-width {np.median(half):.4f} (first 10 states {np.median(half[:10]):.4f}); p25 {np.quantile(half,.25):.3f} p75 {np.quantile(half,.75):.3f}; "
              f"states with half-width > 0.05: {int((half>0.05).sum())} of {n}")
    c = np.mean((cp - plp) ** 2, axis=1); w = weight(cp, plp)
    e_c, e_p = np.mean(cp**2, axis=1), np.mean(plp**2, axis=1)
    far = np.mean(np.abs(plp) > 1.0, axis=1)
    print(f"   at M 200: E_C median {np.median(e_c):.3g}, E_P median {np.median(e_p):.3g}; w* quantiles 10/50/90% {np.round(np.quantile(w,[.1,.5,.9]),3).tolist()}; "
          f"fraction of PLP draws with |e_P| > 1 sigma_x: median {np.median(far):.3f}, max {far.max():.3f}; states with far > 0.1: {int((far>0.1).sum())}; CP-constant states {int((np.ptp(cp,axis=1)==0).sum())}")
    order = np.argsort(halves[200])[::-1][:6]
    for i in order:
        print(f"      state {i:2d}: half-width M200 {halves[200][i]:.3f} (M30 {halves[30][i]:.3f}); w* {w[i]:.3f}; E_C {e_c[i]:.3g}; E_P {e_p[i]:.3g}; c {c[i]:.3g}; far {far[i]:.2f}")
