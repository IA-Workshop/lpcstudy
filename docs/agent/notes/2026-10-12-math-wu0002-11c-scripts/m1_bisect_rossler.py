"""M1: Rossler escape boundary by multisection on divergence (|x| > 1e6), DEVELOPMENT."""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run
LAM = 0.07193978510879935; B = 25.0; N = 3000
delta = 1.0 / (30 * LAM)
data = np.load(__import__("pathlib").Path(__file__).resolve().parent / "esc_rossler.npy")
starts, first, big = data[:, :3], data[:, 3].astype(int), data[:, 5].astype(bool)
good = np.where(~big)[0]; bad = np.where(big)[0]
rng = np.random.default_rng(7)  # DEVELOPMENT literal seed (pair choice only)
worst = []
for trial in range(6):
    a = starts[rng.choice(good)].copy(); b = starts[rng.choice(bad)].copy()
    for it in range(12):
        pts = a + np.linspace(0.0, 1.0, 65)[:, None] * (b - a)
        f, m, g = run("rossler", pts, delta, N, B)
        j = int(np.argmax(g))
        a, b = pts[j - 1].copy(), pts[j].copy()
        if np.max(np.abs(a - b)) < 4 * np.spacing(np.max(np.abs(b))):
            break
    fb, mb, gb = run("rossler", [b], delta, N, B)
    fa, ma, ga = run("rossler", [a], delta, N, B)
    # first step at which the diverging end is non-finite, and |x| at its first failure
    worst.append(fb[0])
    print(f"pair {trial}: |a-b|={np.max(np.abs(a-b)):.1e}; diverging end: first refusal step {fb[0]} "
          f"({fb[0]*delta:.1f} t.u.); non-diverging end: refused={fa[0]>=0} at {fa[0]}, max|x|={ma[0]:.3f}",
          flush=True)
print("worst first refusal of diverging end:", max(worst))
