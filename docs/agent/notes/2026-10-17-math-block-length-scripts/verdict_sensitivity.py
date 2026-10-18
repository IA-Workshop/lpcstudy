"""Would any primary verdict of R1 or R5 change if the block-5 half-widths were widened to block 10/20?

First-order widening of each side of the interval about the point estimate by
f_b = sqrt(max(1, V*(b)/V*(5))) of the criterion's own influence series (b = 10, 20), and by
f_plateau = sqrt(max(1, max_b V*(b)/V*(5))) over b in {8, ..., 30} (the most pessimistic reading).
DEVELOPMENT (DEV-1, DEV-2): a sensitivity of two realizations, not a verdict.
Rules (v3 section 2): H2a(i) pass iff hi < 0.1, fail iff lo >= 0.1; H2a(ii) parts pass iff
(lo, hi) inside (-0.1, 0.1), fail iff entirely outside; H2b(i), H2b(ii) pass iff lo > 0, fail iff
hi <= 0; H3c pass iff hi < 1.05, fail iff lo >= 1.05; H1a pass iff ratio_ci inside [0.75, 1.25],
fail iff entirely outside.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

DIR = Path(sys.argv[1])
RUNS = {"R1": Path(sys.argv[2]), "R5": Path(sys.argv[3])}


def vstar(x: np.ndarray, b: int) -> float:
    xc = x - x.mean()
    w = np.lib.stride_tricks.sliding_window_view(xc, b)
    return float(b * w.mean(axis=1).var())


def verdict(kind: str, lo: float, hi: float) -> str:
    if kind == "upper<0.1":
        return "pass" if hi < 0.1 else ("fail" if lo >= 0.1 else "inconclusive")
    if kind == "inside0.1":
        if -0.1 < lo and hi < 0.1:
            return "pass"
        return "fail" if (lo >= 0.1 or hi <= -0.1) else "inconclusive"
    if kind == "lower>0":
        return "pass" if lo > 0 else ("fail" if hi <= 0 else "inconclusive")
    if kind == "upper<1.05":
        return "pass" if hi < 1.05 else ("fail" if lo >= 1.05 else "inconclusive")
    if kind == "band0.75":
        if 0.75 <= lo and hi <= 1.25:
            return "pass"
        return "fail" if (hi < 0.75 or lo > 1.25) else "inconclusive"
    raise ValueError(kind)


def parts(sysres: dict) -> list[tuple[str, float, float, float, str]]:
    h2a, h2b = sysres["H2a"], sysres["H2b"]
    out = [("H2a(i)", h2a["median_range"], *h2a["range_ci"], "upper<0.1")]
    for p in ("zero", "interior"):
        q = h2a["part_ii"][p]
        out.append((f"H2a(ii) {p}", q["partial_corr"], *q["ci"], "inside0.1"))
    out.append(("H2b(i)", h2b["noise"]["mean_state_spearman"], *h2b["noise"]["ci"], "lower>0"))
    lc = h2b["library_change"]
    out.append(("H2b(ii)", lc["mean_change"], *lc["ci"], "lower>0"))
    out.append(("H3c", sysres["H3c"]["A5_over_A4_mse"], *sysres["H3c"]["ci"], "upper<1.05"))
    for rho, cell in sysres["H1a"]["by_noise"].items():
        out.append((f"H1a rho={float(rho):g}", cell["ratio"], *cell["ratio_ci"], "band0.75"))
    return out


for tag, run in RUNS.items():
    res = json.loads((run / "results.json").read_text())
    z = np.load(DIR / f"series-{tag}.npz")
    changes = 0
    print(f"#### {tag}")
    for system, sysres in res["systems"].items():
        for name, pt, lo, hi, kind in parts(sysres):
            x = z[f"{system}|{name}"]
            v5 = vstar(x, 5)
            ratios = {b: vstar(x, b) / v5 for b in (8, 10, 12, 15, 20, 25, 30)}
            base = verdict(kind, lo, hi)
            row = []
            for label, r in (("b10", ratios[10]), ("b20", ratios[20]),
                             ("plateau", max(ratios.values()))):
                f = math.sqrt(max(1.0, r))
                v = verdict(kind, pt - f * (pt - lo), pt + f * (hi - pt))
                row.append(f"{label} f={f:.3f} {v}")
                changes += v != base
            flag = "  <-- CHANGES" if any(not r.endswith(base) for r in row) else ""
            print(f"  {system:9s} {name:18s} [{lo:+.4f}, {hi:+.4f}] {base:12s} | " + " | ".join(row)
                  + flag)
    print(f"  verdict changes (over 3 widenings x 24 parts): {changes}")
