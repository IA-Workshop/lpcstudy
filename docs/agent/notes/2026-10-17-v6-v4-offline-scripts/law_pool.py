"""Pool the V6 laws and rank the R1 (GPU) values in the GPU-lambda law. No random number.

- CPU lambda: the 2026-10-13 law (D_<system>.npz, 5 perturbed orbits) and the deterministic
  continuation orbit of law_lambda.py (L_<system>_cpu.npz) are pooled; standard error from
  segments of 10^4 window starts (>> an episode), SD / sqrt(n_segments) (normal approximation
  in place of the 2026-10-13 block bootstrap, so that no random number is drawn).
- GPU lambda: L_<system>_gpu.npz (the lambda of R1 and R2). The R1 values are ranked in it.
- The CPU development draws are ranked in both CPU laws (consistency check).
DEVELOPMENT. Usage: python -I law_pool.py <dir with D_*.npz> <v6_dev.npz> <R1 results.json>
"""
import json
import sys

import numpy as np

d_dir, dev_npz, r1_json = sys.argv[1:4]
bar = 1e-3
spacing = {"lorenz63": 45, "rossler": 150, "chua": 150}
dev = np.load(dev_npz)
r1 = json.load(open(r1_json))["systems"]


def windows(D, sp):
    span = 19 * sp + 1
    return [np.lib.stride_tricks.sliding_window_view(row, span)[:, ::sp].max(axis=1) for row in D]


def p_fail(V_rows, seg=10_000):
    fr = np.array([np.mean(r[i:i + seg] >= bar) for r in V_rows
                   for i in range(0, len(r) - seg + 1, seg)])
    return fr.mean(), fr.std(ddof=1) / np.sqrt(len(fr)), len(fr)


for system in ("lorenz63", "rossler", "chua"):
    sp = spacing[system]
    Va = windows(np.load(f"{d_dir}/D_{system}.npz")["D"], sp)
    Vb = windows(np.load(f"L_{system}_cpu.npz")["D"], sp)
    Vg = windows(np.load(f"L_{system}_gpu.npz")["D"], sp)
    pa, pb, pp, pg = p_fail(Va), p_fail(Vb), p_fail(Va + Vb), p_fail(Vg)
    print(f"== {system}")
    for name, (p, se, n) in (("CPU law 2026-10-13 (5 perturbed orbits)", pa),
                             ("CPU law, deterministic continuation", pb),
                             ("CPU law, pooled (2e6 states)", pp),
                             ("GPU-lambda law, deterministic", pg)):
        print(f"  {name:42s} P(V6>=1e-3) {p:.4e}  SE {se:.1e}  approx 95% "
              f"[{max(p - 1.96 * se, 0):.2e}, {p + 1.96 * se:.2e}]  ({n} segments)")
    a, b, g = (np.sort(np.concatenate(x)) for x in (Va, Vb, Vg))
    rk = lambda arr, v: np.searchsorted(arr, v, side="left") / arr.size  # noqa: E731
    v1 = r1[system]["validation"]["integrator_max_dev_sigma"]
    print(f"  R1 (GPU, DEV-1 pilot) V6 {v1:.3e}: rank in GPU-lambda law {rk(g, v1):.4f}; "
          f"in CPU laws {rk(a, v1):.4f} / {rk(b, v1):.4f}")
    for preset in ("pilot", "full"):
        for sid in ("DEV-1", "DEV-2", "DEV-3", "DEV-4"):
            v = float(dev[f"{preset}|{sid}|{system}#v6"])
            print(f"    {preset:5s} {sid} V6 {v:.3e}: rank in CPU law 2026-10-13 {rk(a, v):.4f}, "
                  f"in the deterministic CPU law {rk(b, v):.4f}")
