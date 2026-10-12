"""M3: one-decimal starts near the registry state (0.7, 0, 0) that diverge (DEVELOPMENT)."""
import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run, rk4
grid = np.round(np.arange(-1.5, 1.51, 0.1), 1)
cands = np.array([(0.7 + dx, dy, dz) for dx, dy, dz in itertools.product(
    np.round(np.arange(-1.0, 1.01, 0.1), 1), (-0.5, -0.3, 0.0, 0.3, 0.5), (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5))])
cands = np.round(cands, 1)
first, mx, big = run("chua", cands, 0.1, 5000, 3.0)
sel = np.where((first >= 20) & big)[0]
print(f"{len(cands)} starts, {((first>=0)&big).sum()} diverge, {len(sel)} with k>=20")
rng = np.random.default_rng(3)
out = []
for i in sel:
    p = cands[i]; f = first[i]
    s = p[None].copy(); xs = [abs(p[0])]
    for k in range(f):
        for _ in range(20):
            s = rk4("chua", s, 0.005)
        xs.append(abs(s[0, 0]))
    below = 3 - max(xs[:f]); above = xs[f] - 3
    d = rng.standard_normal((100, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
    fb, _, gb = run("chua", p + 1e-3 * d, 0.1, 5000, 3.0)
    out.append((min(below, above), tuple(p), f, below, above, gb.all(), fb.min(), fb.max()))
out.sort(reverse=True)
for r in out[:10]:
    print(f"start {r[1]} k={r[2]} margin below {r[3]:.4f} above {r[4]:.4f}; 1e-3 ball diverge all {r[5]}, k {r[6]}-{r[7]}")
