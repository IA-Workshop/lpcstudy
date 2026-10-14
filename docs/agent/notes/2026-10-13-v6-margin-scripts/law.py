"""V6 seed law from the per-state deviations D (perstate.py) and the P0/P1 per-state dumps.

V6(seed) = max_{k<20} D(s_{u + spacing k}), u ~ uniform (the test block start is a point of mu, M1).
Exact sliding-block evaluation on each orbit; CI by block bootstrap over orbit segments.
Usage: python -I law.py <D.npz> <spacing> <p0_value> <p1_value>
"""
import sys
import numpy as np
D = np.load(sys.argv[1])["D"]; spacing = int(sys.argv[2]); p0v, p1v = float(sys.argv[3]), float(sys.argv[4])
bar = 1e-3
n_orb, n_per = D.shape
span = 19 * spacing + 1
V = []
for o in range(n_orb):
    win = np.lib.stride_tricks.sliding_window_view(D[o], span)[:, ::spacing]  # (n_u, 20)
    V.append(win.max(axis=1))
V = np.stack(V)  # (n_orb, n_u)
allV = V.ravel()
def ep(x, c):  # exceedance episodes (runs of consecutive states with D >= c)
    e = 0
    for row in x:
        m = row >= c
        e += int(np.sum(m[1:] & ~m[:-1]) + m[0])
    return e
print(f"states {D.size}, per-state P(D>=bar) = {np.mean(D>=bar):.3e} ({np.sum(D>=bar)} states, {ep(D, bar)} episodes)")
print(f"per-state quantiles: 50% {np.quantile(D,.5):.2e} 90% {np.quantile(D,.9):.2e} 99% {np.quantile(D,.99):.2e} 99.9% {np.quantile(D,.999):.2e} max {D.max():.2e}")
qs = [0.5, 0.9, 0.95, 0.99, 0.999]
print("V6 quantiles:", " ".join(f"{q:g}:{np.quantile(allV,q):.2e}" for q in qs))
print(f"P(V6 >= bar) = {np.mean(allV>=bar):.3e};  20*p = {20*np.mean(D>=bar):.3e}")
print(f"rank of P0 value {p0v:.2e}: F = {np.mean(allV < p0v):.3f};  P1 value {p1v:.2e}: F = {np.mean(allV < p1v):.3f}")
for c in (2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2):
    print(f"  P(V6 >= {c:g}) = {np.mean(allV>=c):.3e}   per-state {np.mean(D>=c):.2e}  episodes {ep(D, c)}")
# block bootstrap: segments of 10^4 states (>> episode length); resample segments of V
seg = 10_000
segs = [V[o, i:i+seg] for o in range(n_orb) for i in range(0, V.shape[1]-seg+1, seg)]
fr = np.array([np.mean(s >= bar) for s in segs])
rng = np.random.default_rng(14_0007)
boots = np.array([fr[rng.integers(0, len(fr), len(fr))].mean() for _ in range(4000)])
print(f"P(V6>=bar): {fr.mean():.3e}, block-bootstrap 95% CI [{np.quantile(boots,.025):.2e}, {np.quantile(boots,.975):.2e}], n_segments {len(fr)}, segments with any exceedance {np.sum(fr>0)}")
