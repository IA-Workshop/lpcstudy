"""M1: lingering near the basin boundary, by bisection to float resolution (DEVELOPMENT).

For pairs (bounded start, refused start) from esc_<name>.npy, bisect the segment until the
two ends differ by < 4 ulp, then report the first failing step of the refused end and the
number of steps the refused end spends with |x| <= B after leaving the attractor region.
"""
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run

LAM = {"rossler": 0.07193978510879935, "chua": 0.43113260161336364}
B = {"rossler": 25.0, "chua": 3.0}
N_STEPS = 3_000

for name in ("chua", "rossler"):
    data = np.load(__import__("pathlib").Path(__file__).resolve().parent / f"esc_{name}.npy")
    starts, first, big = data[:, :3], data[:, 3].astype(int), data[:, 5].astype(bool)
    delta = 1.0 / (30 * LAM[name])
    good = np.where(first < 0)[0]
    bad = np.where((first >= 0) & big)[0]
    rng = np.random.default_rng(7)  # DEVELOPMENT literal seed (pair choice only)
    worst = []
    for trial in range(6):
        a = starts[rng.choice(good)].copy(); b = starts[rng.choice(bad)].copy()
        for it in range(12):  # 64-point multisection on the segment
            w = np.linspace(0.0, 1.0, 65)[:, None]
            pts = a + w * (b - a)
            f, _, _ = run(name, pts, delta, N_STEPS, B[name])
            j = int(np.argmax(f >= 0))  # first refused point along the segment (f[64] refused)
            a, b = pts[j - 1].copy(), pts[j].copy()
            if np.max(np.abs(a - b)) < 4 * np.spacing(np.max(np.abs(b))):
                break
        fb, mb, bb = run(name, [b], delta, N_STEPS, B[name])
        fa, ma, ba = run(name, [a], delta, N_STEPS, B[name])
        worst.append(fb[0])
        print(f"{name} pair {trial}: |a-b|={np.max(np.abs(a-b)):.1e} after {it+1} halvings; "
              f"refused end first fail step {fb[0]} ({fb[0]*delta:.1f} t.u.), diverged={bb[0]}; "
              f"bounded end max|x|={ma[0]:.4f}, refused={fa[0] >= 0}", flush=True)
    print(f"{name}: worst first-fail step at float resolution {max(worst)} of {N_STEPS}")

# The 70 Rossler starts refused without diverging: where do they end up?
data = np.load(__import__("pathlib").Path(__file__).resolve().parent / "esc_rossler.npy")
starts, first, big = data[:, :3], data[:, 3].astype(int), data[:, 5].astype(bool)
odd = np.where((first >= 0) & ~big)[0]
delta = 1.0 / (30 * LAM["rossler"])
f2, m2, b2 = run("rossler", starts[odd], delta, 3000, 1e300)
print(f"rossler refused-not-diverged: n={len(odd)}, first fail steps {np.sort(first[odd])[:10]}... "
      f"max {first[odd].max()}; start |x0| range {np.abs(starts[odd,0]).min():.2f}-"
      f"{np.abs(starts[odd,0]).max():.2f}; max|x| over 3000 steps {m2.min():.1f}-{m2.max():.1f}")
from indep import rk4, substeps, MAX_DT
sub = substeps(delta, MAX_DT["rossler"]); dt = delta / sub
s = starts[odd].copy()
for k in range(3000):
    for _ in range(sub):
        s = rk4("rossler", s, dt)
tail = np.zeros(len(odd))
for k in range(3000):
    tail = np.maximum(tail, np.abs(s[:, 0]))
    for _ in range(sub):
        s = rk4("rossler", s, dt)
print(f"  after 3000 steps, max|x| over next 3000 steps: {tail.min():.3f}-{tail.max():.3f} "
      f"(attractor 11.433)")
