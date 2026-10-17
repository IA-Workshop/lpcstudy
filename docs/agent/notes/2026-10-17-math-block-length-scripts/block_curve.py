"""Block-length evidence from the R1 (DEV-1 pilot) and R5 (DEV-2 full) influence series.

DEVELOPMENT (DEV-1, DEV-2): conditional on two realizations; not a hypothesis test of the study.
Reads the series written by extract_series.py (the diagnostics tool's own builders).

For the 24 primary series of each run it prints:
  A. per series V*(b)/V*(1) for b in BLOCKS (V*(1) = the iid variance, ddof 0);
  B. per system and pooled: mean log V*(b)/V*(1) and mean log V*(b)/V*(5), each against a
     permutation null (one permutation per system and draw, applied to all that system's series,
     as the D2 tool does), one-sided upper p;
  C. the null law of the A5 count (V*(10)/V*(5) > 1.1 or V*(20)/V*(5) > 1.15) over the 24
     series, from the same permutations: P(count >= observed);
  D. Politis-White (2004; Patton-Politis-White 2009 correction) automatic block length for the
     circular/moving block bootstrap, per series (an independent algorithm).
Randomness: lpcstudy.data.make_rng(SCRATCH_SEED, "block-length-note", run, system).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, sys.argv[1])  # worktree root, for lpcstudy.data.make_rng
from lpcstudy.data import make_rng  # noqa: E402

DIR = Path(sys.argv[2])
SCRATCH_SEED = 20261017
N_PERM = 2000
BLOCKS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30)
SHOW = (2, 3, 5, 8, 10, 15, 20, 30)


def block_vars(matrix: np.ndarray, b: int) -> np.ndarray:
    """V*(b) of each row: b * var (ddof 0) of the overlapping block means (exact MBB variance)."""
    x = matrix - matrix.mean(axis=-1, keepdims=True)
    cum = np.concatenate([np.zeros(x.shape[:-1] + (1,)), np.cumsum(x, axis=-1)], axis=-1)
    return b * ((cum[..., b:] - cum[..., :-b]) / b).var(axis=-1)


def acf(x: np.ndarray, lags: int) -> np.ndarray:
    xc = x - x.mean()
    d = float(xc @ xc)
    return np.array([1.0] + [float(xc[:-k] @ xc[k:]) / d for k in range(1, lags + 1)])


def politis_white(x: np.ndarray) -> tuple[float, int]:
    """Automatic block length for the circular block bootstrap (PW 2004, PPW 2009).

    m-hat: smallest m with |rho(m+k)| < c sqrt(log10 n / n) for k = 1..K_n, c = 2,
    K_n = max(5, ceil(sqrt(log10 n))); M = 2 m-hat; flat-top (trapezoid) lag window.
    b = (2 G^2 / D_CB)^(1/3) n^(1/3), D_CB = (4/3) g(0)^2, G = sum lambda(k/M) |k| R(k),
    g(0) = sum lambda(k/M) R(k). Returns (b, m-hat).
    """
    n = x.size
    kn = max(5, math.ceil(math.sqrt(math.log10(n))))
    mmax = math.ceil(math.sqrt(n)) + kn
    r = acf(x, mmax + kn)
    thr = 2.0 * math.sqrt(math.log10(n) / n)
    mhat = mmax
    for m in range(0, mmax + 1):
        if np.all(np.abs(r[m + 1:m + 1 + kn]) < thr):
            mhat = m
            break
    big_m = min(2 * mhat, mmax)
    xc = x - x.mean()
    cov = np.array([float(xc[:n - k] @ xc[k:]) / n for k in range(big_m + 1)])
    if big_m == 0:
        return 1.0, mhat
    t = np.arange(big_m + 1) / big_m
    lam = np.where(t <= 0.5, 1.0, 2.0 * (1.0 - t))
    g0 = cov[0] + 2.0 * float(np.sum(lam[1:] * cov[1:]))
    big_g = 2.0 * float(np.sum(lam[1:] * np.arange(1, big_m + 1) * cov[1:]))
    if g0 <= 0:
        return float("nan"), mhat
    b = (2.0 * big_g ** 2 / ((4.0 / 3.0) * g0 ** 2)) ** (1.0 / 3.0) * n ** (1.0 / 3.0)
    return max(1.0, b), mhat


def main() -> None:
    combined = {}
    for tag in ("R1", "R5"):
        z = np.load(DIR / f"series-{tag}.npz")
        meta = json.loads((DIR / f"series-{tag}.json").read_text())
        prim = [e for e in meta["series"] if e["primary"]]
        systems = sorted({e["system"] for e in prim}, key=["lorenz63", "rossler", "chua"].index)
        print(f"\n######## {tag} ({meta['seed_id']}), {len(prim)} primary series")
        print("A. V*(b)/V*(1) per series; PW = Politis-White CB block length (m-hat)")
        print(f"  {'series':34s} n    " + " ".join(f"b={b:<4d}" for b in SHOW) + "  PW")
        obs_log = {}      # key -> array over BLOCKS of log V*(b)/V*(1)
        a5_obs = 0
        pw = []
        for e in prim:
            x = z[e["key"]]
            v = np.array([block_vars(x[None, :], b)[0] for b in BLOCKS])
            obs_log[e["key"]] = np.log(v / v[0])
            r10, r20 = v[BLOCKS.index(10)] / v[BLOCKS.index(5)], v[BLOCKS.index(20)] / v[BLOCKS.index(5)]
            a5_obs += bool(r10 > 1.1 or r20 > 1.15)
            b_pw, mhat = politis_white(x)
            pw.append(b_pw)
            print(f"  {e['key']:34s} {e['n']:4d} " + " ".join(
                f"{v[BLOCKS.index(b)] / v[0]:6.3f}" for b in SHOW) + f"  {b_pw:5.2f} ({mhat})")
        print(f"  Politis-White b: median {np.median(pw):.2f}, max {np.max(pw):.2f}, "
              f"share > 5: {np.mean(np.array(pw) > 5):.3f}")
        # permutation null, one permutation per system and draw
        null_log = {}
        a5_null = np.zeros(N_PERM, dtype=int)
        for system in systems:
            ser = [e for e in prim if e["system"] == system]
            n_max = max(e["n"] for e in ser)
            keys = make_rng(SCRATCH_SEED, "block-length-note", tag, system).random((N_PERM, n_max))
            for e in ser:
                x = z[e["key"]]
                perm = x[np.argsort(keys[:, :x.size], axis=1)]
                v = np.stack([block_vars(perm, b) for b in BLOCKS], axis=1)
                null_log[e["key"]] = np.log(v / v[:, :1])
                i5, i10, i20 = BLOCKS.index(5), BLOCKS.index(10), BLOCKS.index(20)
                a5_null += ((v[:, i10] / v[:, i5] > 1.1) | (v[:, i20] / v[:, i5] > 1.15)).astype(int)
        print(f"C. A5 count: observed {a5_obs} of {len(prim)}; permutation null mean "
              f"{a5_null.mean():.2f}, SD {a5_null.std():.2f}, P(count >= {a5_obs}) "
              f"{(1 + np.sum(a5_null >= a5_obs)) / (1 + N_PERM):.3f}, P(count >= 1) "
              f"{np.mean(a5_null >= 1):.3f}")
        print("B. mean log V*(b)/V*(1) [and mean log V*(b)/V*(5)]: observed, null mean, null 0.99q, p")
        groups = [(s, [e["key"] for e in prim if e["system"] == s]) for s in systems]
        groups.append(("pooled", [e["key"] for e in prim]))
        for label, keys_ in groups:
            o = np.mean([obs_log[k] for k in keys_], axis=0)
            nl = np.mean([null_log[k] for k in keys_], axis=0)
            combined.setdefault(label, []).append((o, nl))
            print(f"  {label}")
            for b in SHOW:
                i, i5 = BLOCKS.index(b), BLOCKS.index(5)
                p1 = (1 + np.sum(nl[:, i] >= o[i])) / (1 + N_PERM)
                d5o, d5n = o[i] - o[i5], nl[:, i] - nl[:, i5]
                p5 = (1 + np.sum(d5n >= d5o)) / (1 + N_PERM)
                print(f"    b={b:2d}  vs b=1: {o[i]:+.4f} (null {nl[:, i].mean():+.4f}, "
                      f"q99 {np.quantile(nl[:, i], 0.99):+.4f}, p {p1:.3f})"
                      + ("" if b <= 5 else
                         f"   vs b=5: {d5o:+.4f} (null {d5n.mean():+.4f}, q99 "
                         f"{np.quantile(d5n, 0.99):+.4f}, p {p5:.3f})"))
    print("\n######## R1 and R5 together (independent seeds; equal-weight mean of the two runs)")
    for label, pair in combined.items():
        o = (pair[0][0] + pair[1][0]) / 2.0
        nl = (pair[0][1] + pair[1][1]) / 2.0   # independent permutations: the null of the mean
        print(f"  {label}")
        for b in (5, 10, 20, 30):
            i, i5 = BLOCKS.index(b), BLOCKS.index(5)
            p1 = (1 + np.sum(nl[:, i] >= o[i])) / (1 + N_PERM)
            excess = o[i] - nl[:, i].mean()
            line = (f"    b={b:2d} vs 1: excess over null {excess:+.4f} (factor {math.exp(excess):.3f};"
                    f" null SD {nl[:, i].std():.4f}), p {p1:.3f}")
            if b > 5:
                d5o, d5n = o[i] - o[i5], nl[:, i] - nl[:, i5]
                p5 = (1 + np.sum(d5n >= d5o)) / (1 + N_PERM)
                ex5 = d5o - d5n.mean()
                line += (f";  vs 5: excess {ex5:+.4f} (factor {math.exp(ex5):.3f}; null SD "
                         f"{d5n.std():.4f}; one-sided 95% upper factor "
                         f"{math.exp(ex5 + 1.645 * d5n.std()):.3f}), p {p5:.3f}")
            print(line)


if __name__ == "__main__":
    main()
