#!/usr/bin/env python3
"""WU-0041b, M-5 and M-6: R^2 on a target censored at a fixed cap, and the
empty-set baseline.

Part A (synthetic, analytic conditional means, Monte Carlo over X only):
Z = b1 X1 + b2 X2 + s e, X ~ N(0, I), e ~ N(0, 1), Y = min(Z, c) with c set
to the (1 - p_c) quantile of Z. The best predictor given a subset S is
E[min(Z, c) | X_S] = m Phi(a) - v phi(a) + c (1 - Phi(a)), a = (c - m) / v,
with m, v the conditional mean and SD of Z given X_S. Reported: R^2 and the
gain Delta R^2 of X2 (and of X1) on Y, against the uncensored values.

Part B (DEVELOPMENT, DEV-2 full dumps, run commit 6f1a8c8, stored leaves
``qn/oracle/log_horizon/*``): the censored count of the Q-N horizon target on
the frozen systems, and the expected size of R^2 of the training-mean
predictor, -(1/n_train + 1/n_test) x (long-run variance factor).

Run: ``<.venv>/bin/python -I censoring_r2.py`` (numpy only; CPU, 1 thread).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

SQ2 = math.sqrt(2.0)


def ncdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / SQ2))


def npdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def cens_mean(m: np.ndarray, v: float, c: float) -> np.ndarray:
    a = (c - m) / v
    return m * ncdf(a) - v * npdf(a) + c * (1.0 - ncdf(a))


def part_a() -> None:
    rng = np.random.default_rng(20261025)
    n = 400_000
    x1, x2, e = rng.standard_normal((3, n))
    print("## A. Synthetic: Delta R^2 under censoring at a fixed cap\n")
    print("| b1, b2, s | p_c | R2 full | dR2(X2) | dR2(X2) / uncensored |"
          " dR2(X1) / uncensored |")
    print("|---|---|---|---|---|---|")
    for b1, b2, s in ((1.0, 1.0, 1.0), (1.0, 0.5, 1.0), (1.0, 0.2, 1.0)):
        z = b1 * x1 + b2 * x2 + s * e
        var_z = b1 * b1 + b2 * b2 + s * s
        unc_x2 = b2 * b2 / var_z
        unc_x1 = b1 * b1 / var_z
        for p_c in (0.0, 0.05, 0.125, 0.25, 0.5):
            c = np.inf if p_c == 0 else float(np.quantile(z, 1 - p_c))
            y = np.minimum(z, c)
            vy = y.var()
            if p_c == 0:
                pf, p1, p2 = b1 * x1 + b2 * x2, b1 * x1, b2 * x2
            else:
                pf = cens_mean(b1 * x1 + b2 * x2, s, c)
                p1 = cens_mean(b1 * x1, math.hypot(b2, s), c)
                p2 = cens_mean(b2 * x2, math.hypot(b1, s), c)
            r2 = lambda p: 1 - np.mean((y - p) ** 2) / vy  # noqa: E731
            d2 = r2(pf) - r2(p1)
            d1 = r2(pf) - r2(p2)
            print(f"| {b1}, {b2}, {s} | {p_c} | {r2(pf):.3f} | {d2:.4f} |"
                  f" {d2/unc_x2:.3f} | {d1/unc_x1:.3f} |")


def part_b(dump_dir: Path) -> None:
    print("\n## B. DEVELOPMENT (DEV-2): censoring of the Q-N horizon target\n")
    cap = math.log(240.0)
    for system in ("lorenz63", "rossler", "chua"):
        z = np.load(dump_dir / f"{system}.npz")
        y = z["qn/oracle/log_horizon/y"]
        n_c = int(np.sum(y >= cap - 1e-12))
        p3 = z["qn/oracle/log_horizon/pred3"]
        p4 = z["qn/oracle/log_horizon/pred4"]
        tot = np.sum((y - y.mean()) ** 2)
        r3 = 1 - np.sum((y - p3) ** 2) / tot
        r4 = 1 - np.sum((y - p4) ** 2) / tot
        print(f"- {system}: n_test {y.size}, censored at 240 steps {n_c}; "
              f"max y {np.exp(y.max()):.0f} steps; R2(F3) {r3:.3f}, "
              f"R2(F4) {r4:.3f}, dR2 {r4 - r3:+.4f}")
    print("\n## C. Expected R^2 of the training-mean predictor\n")
    for lrv in (1.0, 2.0, 4.0):
        print(f"- n_train 3000, n_test 1000, long-run variance factor {lrv}: "
              f"E R2(empty) = {-(1/3000 + 1/1000) * lrv:.4f}")


def main() -> None:
    part_a()
    if len(sys.argv) > 1:
        part_b(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
