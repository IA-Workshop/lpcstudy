"""S4 Hindmarsh-Rose burst structure at the study's Delta (DEVELOPMENT):
spikes = local maxima of x above a threshold between the quiet level and the
spike peaks; a burst = spikes separated by less than a gap; reports spikes per
burst, burst duration, inter-burst interval and the quiet-phase fraction in
steps and LT, against Delta, the delay window (D-1) tau and the 1-LT window."""

import jax.numpy as jnp
import numpy as np

from lpcstudy.embedding import select_delay
from lpcstudy.systems import lyapunov_guarded, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

LT = 30
sp = CANDIDATES["S4"]()
lam, _ = lyapunov_guarded(sp, 20 * sp.max_dt, 100_000, 5_000)
interval = 1.0 / (LT * lam)
step = make_flow_step(sp, sp.params, interval)
orbit = simulate_trajectory(step, jnp.asarray(sp.initial_state), 3000 + 200_000)[3000:]
x = orbit[:, 0]
print(f"S4: Delta {interval:.5f}, 200000 steps = {200000*interval:.0f} time units; x quantiles 1/10/50/90/99% {np.array2string(np.quantile(x, [.01,.1,.5,.9,.99]), precision=3)}; "
      f"z (slow) range [{orbit[:,2].min():.3f}, {orbit[:,2].max():.3f}]")
hist, edges = np.histogram(x, bins=20)
print("  x histogram counts:", hist.tolist(), "edges", np.array2string(edges, precision=2))
thr = 0.5 * (np.quantile(x, 0.5) + x.max())
peaks = np.nonzero((x[1:-1] > x[:-2]) & (x[1:-1] >= x[2:]) & (x[1:-1] > thr))[0] + 1
isi = np.diff(peaks)
print(f"  spike threshold {thr:.3f}; {len(peaks)} spikes; inter-spike interval (steps) quantiles 10/50/90% {np.array2string(np.quantile(isi, [.1,.5,.9]), precision=1)}")
gap = 3 * np.median(isi)
starts = np.concatenate([[0], np.nonzero(isi > gap)[0] + 1])
ends = np.concatenate([np.nonzero(isi > gap)[0], [len(peaks) - 1]])
n_spikes = ends - starts + 1
durations = peaks[ends] - peaks[starts]
ibi = peaks[starts[1:]] - peaks[ends[:-1]]
obs_norm = (x - x.mean()) / x.std()
tau = select_delay(obs_norm, max_lag=3 * LT)
print(f"  burst gap {gap:.0f} steps; {len(starts)} bursts; spikes per burst median {np.median(n_spikes):.0f} (p10 {np.quantile(n_spikes,.1):.0f}, p90 {np.quantile(n_spikes,.9):.0f}); "
      f"burst duration median {np.median(durations):.0f} steps = {np.median(durations)/LT:.2f} LT; quiet interval median {np.median(ibi):.0f} steps = {np.median(ibi)/LT:.2f} LT (p90 {np.quantile(ibi,.9)/LT:.2f} LT); "
      f"burst period median {np.median(np.diff(peaks[starts]))/LT:.2f} LT; quiet fraction of time {ibi.sum()/len(x):.2f}")
print(f"  AMI delay {tau} -> tau {min(tau, 5)}; window (D-1)tau = {6*min(tau,5)} steps against spike interval {np.median(isi):.0f} steps and burst period {np.median(np.diff(peaks[starts])):.0f} steps")
