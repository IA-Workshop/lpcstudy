"""Units of S1, S2, S3 exactly as ``data.build_context`` derives them
(DEVELOPMENT, one thread): the statistics orbit from the registry start
(burn-in 100 LT = 3000 steps, then 200 000 steps at Delta), sigma_x, the
invariant covariance and its eigenvalues (whitening scale), the AMI delay and
its cap, the ACF time, the spacing, the split layout and trajectory lengths for
the presets, the orbit maxima, and three per-state oracle distributions on
thinned states: nu (D = 7), Lambda_tilde = 30 Lambda_bar over 1 LT, and the
Levina-Bickel inverse dimension 1/d_LB (k = 20, pool 20 000).
Delta uses the exponent the code would cache (lyapunov_guarded at
20 max_dt, 100 000 steps, burn 5 000).
"""

import math
import sys
import time

import jax.numpy as jnp
import numpy as np

from lpcstudy.config import FULL, PILOT, SMOKE
from lpcstudy.data import _symmetric_root
from lpcstudy.dynamics import growth_exponent, make_amplification, make_observability
from lpcstudy.embedding import autocorrelation_time, select_delay
from lpcstudy.oracle import inverse_dimension, local_dimension_counted
from lpcstudy.systems import lyapunov_guarded, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

LT = 30


def layout(cfg, history, spacing, max_lib):
    horizon_max = cfg.horizon_max
    gap = cfg.theiler_window + history + horizon_max
    library_len = history + max_lib + horizon_max + 1
    cursor = library_len + gap
    for n in (cfg.n_construction, cfg.n_calibration, cfg.n_test):
        start = cursor + history
        cursor = int(start + spacing * (n - 1)) + horizon_max + gap
    return cursor, library_len


which = sys.argv[1:] or list(CANDIDATES)
for key in which:
    sp = CANDIDATES[key]()
    t0 = time.time()
    import os
    steps = {"S1": 1_000_000, "S2": 4_000_000, "S3": 1_000_000}.get(key, 100_000) if os.environ.get("LYAP_LONG") else 100_000
    lam, lyap_max = lyapunov_guarded(sp, 20 * sp.max_dt, steps, 5_000)
    print(f"[{key}] Benettin steps {steps}")
    interval = 1.0 / (LT * lam)
    substeps = math.ceil(interval / sp.max_dt)
    step = make_flow_step(sp, sp.params, interval)
    burn = int(FULL.burn_in_lyapunov * LT)
    stats_full = simulate_trajectory(step, jnp.asarray(sp.initial_state), burn + 200_000)
    stats = stats_full[burn:]
    print(f"[{key}] {sp.name}: lambda(code cache) {lam!r}, Delta {interval:.6f}, substeps {substeps}, dt {interval/substeps:.6f}")
    print(f"  orbit maxima |s_i|: lyapunov orbit max|x| {lyap_max:.3f}; statistics orbit (burn-in included) "
          f"{np.array2string(np.abs(stats_full).max(axis=0), precision=3)}; bound {sp.orbit_bound}")
    obs = stats[:, sp.observed_index]
    mean, scale = float(obs.mean()), float(obs.std())
    cov = np.cov(stats.T)
    eig = np.linalg.eigvalsh(cov)
    whiten, unwhiten = _symmetric_root(cov)
    print(f"  observable: mean {mean:.5f}, sigma_x {scale:.5f}; state mean {np.array2string(stats.mean(axis=0), precision=4)}")
    print(f"  state std per coordinate {np.array2string(np.sqrt(np.diag(cov)), precision=4)}; covariance eigenvalues {np.array2string(eig, precision=5)}; "
          f"condition {eig.max()/eig.min():.1f}; whitening scale sqrt(eig) {np.array2string(np.sqrt(eig), precision=4)}")
    q = np.quantile(obs, [0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999])
    print(f"  observable quantiles 0.1/1/10/50/90/99/99.9%: {np.array2string(q, precision=3)}; skewness {float(((obs-mean)**3).mean()/scale**3):.3f}; "
          f"kurtosis {float(((obs-mean)**4).mean()/scale**4):.2f}")
    obs_norm = (obs - mean) / scale
    ami = select_delay(obs_norm, max_lag=3 * LT)
    dim = FULL.embedding_dim
    delay = max(1, int(round(min(ami, LT // (dim - 1)))))
    acf = autocorrelation_time(obs_norm, max_lag=50 * LT)
    eff = min(acf, LT)
    spacing = max(int(math.ceil(FULL.thinning_factor * eff)), FULL.theiler_window)
    history = (dim - 1) * delay
    print(f"  AMI first minimum {ami} steps -> delay tau {delay} (cap {LT // (dim - 1)}); window (D-1)tau = {history} steps = {history/LT:.2f} LT")
    print(f"  ACF 1/e envelope time {acf} steps ({acf/LT:.2f} LT; max_lag {50*LT}); effective min(acf, 30) = {eff}; spacing {spacing} steps = {spacing/LT:.2f} LT; "
          f"block of 5 states = {5*spacing/LT:.1f} LT")
    for cfg in (SMOKE, PILOT, FULL):
        total, lib = layout(cfg, history, spacing, max(cfg.library_sizes))
        est = history + 5 * cfg.estimator_pairs + 1
        rk4 = (2 * burn + total + est) * substeps
        print(f"  preset {cfg.name}: main trajectory {total} steps (library segment {lib}), estimator trajectory {est}, "
              f"RK4 substeps (stats+main+est, burn-in included) {rk4/1e6:.1f} M, x dim {sp.dim}")
    # per-state oracles on thinned states
    n_states = 2000
    times = history + spacing * np.arange(n_states)
    times = times[times + LT < len(stats)]
    nu_fn = make_observability(step, sp.observed_index, scale, whiten, delay, dim)
    amp_fn = make_amplification(step, sp.observed_index, scale, unwhiten, LT)
    nu = np.asarray(nu_fn(jnp.asarray(stats[times - history])))
    gains = np.asarray(amp_fn(jnp.asarray(stats[times])))
    growth = growth_exponent(gains, LT) * LT
    qs = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
    print(f"  nu (D {dim}, tau {delay}) on {len(times)} thinned states: quantiles 1/5/25/50/75/95/99% = "
          f"{np.array2string(np.quantile(nu, qs), precision=3)}; max {nu.max():.3g}; non-finite {int((~np.isfinite(nu)).sum())}; "
          f"ratio p99/p1 {np.quantile(nu, .99)/np.quantile(nu, .01):.1f}")
    print(f"  Lambda_tilde = 30 * slope of ln g_H over 1 LT: quantiles = {np.array2string(np.quantile(growth, qs), precision=3)}; "
          f"mean {growth.mean():.3f}; fraction < 0.3: {np.mean(growth < 0.3):.3f}; fraction > 1.5: {np.mean(growth > 1.5):.3f}")
    hist, _ = np.histogram(growth, bins=np.linspace(-1, 4, 21))
    print(f"  Lambda_tilde histogram (bins of 0.25 from -1 to 4): {hist.tolist()}")
    print(f"  g_H at 1 LT: median {np.median(gains[:, -1]):.3g}, p5 {np.quantile(gains[:, -1], .05):.3g}, p95 {np.quantile(gains[:, -1], .95):.3g}")
    # Levina-Bickel inverse dimension, as oracle.state_oracles does it
    # pool from the first half of the orbit, queries from the second half
    # (disjoint, as library_states and eval_states are in the code)
    rng = np.random.default_rng(20261020)
    half = len(stats) // 2
    pool_idx = rng.choice(half, size=20_000, replace=False)
    w_pool = (stats[pool_idx] - stats.mean(axis=0)) @ whiten.T
    q_times = half + history + spacing * np.arange(n_states)
    q_times = q_times[q_times < len(stats)]
    w_q = (stats[q_times] - stats.mean(axis=0)) @ whiten.T
    dims, floored = local_dimension_counted(w_pool, w_q)
    inv = inverse_dimension(dims)
    ok = np.isfinite(inv)
    print(f"  Levina-Bickel (k 20, pool 20000): 1/d_LB mean {inv[ok].mean():.4f} (se {inv[ok].std(ddof=1)/math.sqrt(ok.sum()):.4f}), "
          f"d = {1/inv[ok].mean():.3f}; floored {int(floored.sum())}; non-finite {int((~ok).sum())}")
    # delay-map Jacobian rank at D = 7: smallest/largest singular value of A (7 x m)
    print(f"  [{time.time()-t0:.0f} s]")
    print()
