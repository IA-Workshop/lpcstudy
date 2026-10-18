"""Coverage and half-width of the moving-block interval against the block length (first order).

Model: the influence series psi_i of a criterion (its interval is, to first order, the mean of
psi +- z sqrt(V*(b)/n), with V*(b) the exact MBB variance). Gaussian series, five dependence
models; the true variance of the mean is exact from the autocovariance. Scratch randomness via
lpcstudy.data.make_rng(SCRATCH_SEED, "block-length-note", "coverage", model, n).

Models (x = sqrt(1-w) e + sqrt(w) u, e iid N(0,1), u stationary AR(1) unit variance):
  iid           w = 0
  AR(1) 0.1     AR(1) with phi = 0.1 (w = 1, phi_u = 0.1)
  AR(1) 0.3     AR(1) with phi = 0.3 (the WU-0006 stress case)
  L63-H1a-like  w = 0.125, phi_u = 0.8  (acf ~ 0.10, 0.08, 0.064 ...; V*(5)/V*(1) ~ 1.33,
                long-run factor 2.0: matched to R5 Lorenz-63 H1a rho=0.01)
  slow-weak     w = 0.01, phi_u = 0.95 (acf1 ~ 0.0095, invisible to D1; V*(20)/V*(5) ~ 1.09:
                matched to the pooled R1+R5 Rossler excess)
Levels: 95% (z 1.95996) and 1 - 0.05/3 (z 2.39398). R = 20000 per cell; MC SE of a coverage
near 0.95 is 0.0015, near 0.983 is 0.0009.
"""
from __future__ import annotations

import math
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
from lpcstudy.data import make_rng  # noqa: E402

SCRATCH_SEED = 20261017
R, CHUNK = 20000, 2500
BLOCKS = (1, 5, 8, 10, 15, 20)
Z = {"95%": 1.959963984540054, "98.3%": 2.3939797998185104}
MODELS = {"iid": (0.0, 0.0), "AR(1) 0.1": (1.0, 0.1), "AR(1) 0.3": (1.0, 0.3),
          "L63-H1a-like": (0.125, 0.8), "slow-weak": (0.01, 0.95)}


def true_nvar(w: float, phi: float, n: int) -> float:
    """n Var(mean) exactly: sum_{|k|<n} (1 - |k|/n) gamma(k)."""
    k = np.arange(1, n)
    gamma = w * phi ** k
    return 1.0 + 2.0 * float(np.sum((1.0 - k / n) * gamma))


def expected_vstar(w: float, phi: float, n: int, b: int) -> float:
    """Leading-order E V*(b)/gamma(0) ignoring the O(b/n) centring bias: sum_{|k|<b}(1-|k|/b)gamma."""
    k = np.arange(1, b)
    return 1.0 + 2.0 * float(np.sum((1.0 - k / b) * w * phi ** k))


def simulate(w: float, phi: float, n: int, rng: np.random.Generator) -> np.ndarray:
    e = rng.standard_normal((CHUNK, n))
    if w == 0.0:
        return e
    eta = rng.standard_normal((CHUNK, n))
    u = np.empty((CHUNK, n))
    u[:, 0] = eta[:, 0]
    s = math.sqrt(1.0 - phi * phi)
    for t in range(1, n):
        u[:, t] = phi * u[:, t - 1] + s * eta[:, t]
    return math.sqrt(1.0 - w) * e + math.sqrt(w) * u


def vstar(x: np.ndarray, b: int) -> np.ndarray:
    xc = x - x.mean(axis=1, keepdims=True)
    cum = np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(xc, axis=1)], axis=1)
    return b * ((cum[:, b:] - cum[:, :-b]) / b).var(axis=1)


def main() -> None:
    for name, (w, phi) in MODELS.items():
        for n in (300, 500, 1000):
            tv = true_nvar(w, phi, n)
            rng = make_rng(SCRATCH_SEED, "block-length-note", "coverage", name, n)
            cover = {b: {lv: 0 for lv in Z} for b in BLOCKS}
            ratio = {b: [] for b in BLOCKS}
            for _ in range(R // CHUNK):
                x = simulate(w, phi, n, rng)
                m = x.mean(axis=1) * math.sqrt(n)   # sqrt(n) * mean; true mean 0
                for b in BLOCKS:
                    v = vstar(x, b)
                    ratio[b].append(v / tv)
                    for lv, z in Z.items():
                        cover[b][lv] += int(np.sum(np.abs(m) <= z * np.sqrt(v)))
            print(f"{name:13s} n={n:4d} true n Var(mean) {tv:.3f}")
            for b in BLOCKS:
                rr = np.concatenate(ratio[b])
                print(f"   b={b:2d}  cov95 {cover[b]['95%'] / R:.4f}  cov98.3 {cover[b]['98.3%'] / R:.4f}"
                      f"  E[V*/V] {rr.mean():.3f} (first order {expected_vstar(w, phi, n, b) / tv:.3f})"
                      f"  SD[V*/V] {rr.std():.3f}  mean hw/true {np.mean(np.sqrt(rr)):.3f}")


if __name__ == "__main__":
    main()
