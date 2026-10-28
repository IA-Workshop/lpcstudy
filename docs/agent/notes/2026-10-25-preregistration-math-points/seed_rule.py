#!/usr/bin/env python3
"""WU-0041b, M-1: error and power of the all-three-seeds rule.

DEVELOPMENT (DEV-1, DEV-3, DEV-4): not a hypothesis test. Method diagnostic of
the premise of the p^3 bound, not a reported result; no seed-to-seed spread of
any QoI is reported (schedule O7): the per-pair z values are the project's own
two-run comparison statistic (v3 section 9 item 3, ``compare_runs.td_part``).

Inputs: the stored leaves printed by the ensemble summary's ``extract.py``
(``../2026-10-23-extension-ensemble-summary/extract.out.md``). Standard library
only. Run: ``python3 -I seed_rule.py`` from this folder.

Parts:
1. Per-seed error bounds (nominal and under the WU-0006 undercoverage), the
   p^3 product, and the multi-part (union) correction for "fail" words.
2. Word stability across DEV-1/3/4 for the 36 per-system words (12 criteria x
   3 frozen systems), and the decisive share per seed versus promoted.
3. Pairwise z (z_sym, z_away) for the 18 primary parts x 3 seed pairs; mean
   z_sym^2 estimates 1 + tau^2/SE^2 (tau: between-seed SD of the estimand).
4. Power of the rule: per-seed decision probability pi -> pi^3, and the
   distance from the band edge needed for 80% power, one seed versus three.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path
from statistics import NormalDist

N = NormalDist()
SRC = Path(__file__).resolve().parent.parent / (
    "2026-10-23-extension-ensemble-summary/extract.out.md"
)
PRIMARY = 1 - 0.05 / 3


def section(text: str, title: str) -> list[str]:
    """Return the table lines of the section ``## title``."""
    out, on = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            on = line[3:].strip() == title
            continue
        if on and line.startswith("|"):
            out.append(line)
    return out


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def part1() -> None:
    print("## 1. Per-seed one-sided error and the p^3 product\n")
    # WU-0006 reference coverage (tests/slow/test_statistics_coverage.py):
    # phi = 0: 0.9451 / 0.9800; phi = 0.3: 0.9257-0.9292 / 0.9695-0.9732.
    rows = [
        ("secondary 95%, nominal", 0.025),
        ("secondary 95%, phi=0 (cov 0.945)", (1 - 0.945) / 2),
        ("secondary 95%, phi=0.3 (cov 0.926)", (1 - 0.9257) / 2),
        ("primary 98.3%, nominal", 0.05 / 6),
        ("primary 98.3%, phi=0 (cov 0.980)", (1 - 0.980) / 2),
        ("primary 98.3%, phi=0.3 (cov 0.9695)", (1 - 0.9695) / 2),
    ]
    print("| case | p per seed | p^3 | (2p)^3 | (3p)^3 |")
    print("|---|---|---|---|---|")
    for name, p in rows:
        print(
            f"| {name} | {p:.4f} | {p**3:.2e} | {(2*p)**3:.2e} |"
            f" {(3*p)**3:.2e} |"
        )
    # Family sums (union bound over promoted words), k = parts of a criterion
    # for a false "fail" (union over parts); a false "pass" needs one false
    # part, so k = 1 for pass.
    # Primaries per system: H2a 3 parts (4 if w*=1 > 5%), H2b 2, H3c 1.
    # Secondaries per system (parts): H1a 2 (rho 1%, 2%), H1b 1, H1c 1,
    # H1d 3, H2c 2, H2d 1, H2e 2, H3a (no fail word; FWER-type pass 0.01),
    # H3b 2.
    prim_k = [4, 2, 1]
    sec_k = [2, 1, 1, 3, 2, 1, 2, 2]
    for label, p_prim, p_sec in (
        ("nominal", 0.05 / 6, 0.025),
        ("undercoverage phi=0.3", (1 - 0.9695) / 2, (1 - 0.9257) / 2),
    ):
        fam = 6 * (sum((k * p_prim) ** 3 for k in prim_k)
                   + sum((k * p_sec) ** 3 for k in sec_k) + 0.013 ** 3)
        fam1 = 6 * (3 * p_prim ** 3 + 9 * p_sec ** 3)
        print(
            f"\nFamily (6 systems x 12 criteria, false fail with union over "
            f"parts, H3a at FWER 0.013), {label}: {fam:.2e}"
            f" (false pass words only, k = 1: {fam1:.2e})"
        )
    # The same family sum with a seed-dependent estimand (tau = 0.8 SE, the
    # value that part 3 measures), judged against the seed-mean estimand.
    for label, cov_p, cov_s in (
        ("tau=0.8, nominal coverage", 0.05 / 6, 0.025),
        ("tau=0.8, undercoverage phi=0.3", (1 - 0.9695) / 2,
         (1 - 0.9257) / 2),
    ):
        tau = 0.8
        p_prim = N.cdf(N.inv_cdf(cov_p) / (1 + tau * tau) ** 0.5)
        p_sec = N.cdf(N.inv_cdf(cov_s) / (1 + tau * tau) ** 0.5)
        fam = 6 * (sum((k * p_prim) ** 3 for k in prim_k)
                   + sum((k * p_sec) ** 3 for k in sec_k) + 0.013 ** 3)
        print(f"Family, {label}: p_prim {p_prim:.4f}, p_sec {p_sec:.4f}, "
              f"family {fam:.2e}")
        fam1 = 6 * (3 * p_prim ** 3 + 9 * p_sec ** 3)
        print(f"  (false pass words only, k = 1: {fam1:.2e})")
    # Between-seed variation of the estimand (tau, in SE units): per-seed
    # false-pass rate against the across-seed mean estimand at the edge.
    print("\nPer-seed false-pass rate against the seed-mean estimand, "
          "estimand SD tau (in SE units):")
    for z, lab in ((N.inv_cdf(1 - 0.05 / 6), "primary"),
                   (N.inv_cdf(0.975), "secondary")):
        vals = []
        for t in (0.0, 0.5, 1.0, 1.5):
            p = N.cdf(-z / (1 + t * t) ** 0.5)
            vals.append(f"tau={t}: p={p:.4f}, p^3={p**3:.1e}")
        print(f"- {lab}: " + "; ".join(vals))


def part2(text: str) -> None:
    print("\n## 2. Word stability, frozen systems, DEV-1/3/4\n")
    lines = section(text, "Words: ensemble")
    head = cells(lines[0])
    cols = head[1:]
    stable = decisive_stable = stable_inc = 0
    per_seed_decisive = {"DEV-1": 0, "DEV-3": 0, "DEV-4": 0}
    total = 0
    pass_fail_flip = 0
    for line in lines[2:]:
        c = cells(line)
        if c[0] in ("Q-N", "gain_bound"):
            continue
        words = dict(zip(cols, c[1:]))
        for system in ("lorenz63", "rossler", "chua"):
            ws = [words[f"ens-{s}:{system}"] for s in per_seed_decisive]
            total += 1
            for s, w in zip(per_seed_decisive, ws):
                per_seed_decisive[s] += w in ("pass", "fail")
            if len(set(ws)) == 1:
                stable += 1
                if ws[0] in ("pass", "fail"):
                    decisive_stable += 1
                else:
                    stable_inc += 1
            if "pass" in ws and "fail" in ws:
                pass_fail_flip += 1
    mean_dec = sum(per_seed_decisive.values()) / 3
    print(f"- per-system words: {total}; same on all three seeds: {stable} "
          f"({stable/total:.2f}); of these decisive {decisive_stable}, "
          f"inconclusive {stable_inc}")
    print(f"- decisive (pass or fail) per seed: {per_seed_decisive}; "
          f"mean {mean_dec:.1f} of {total} ({mean_dec/total:.2f})")
    print(f"- promoted decisive {decisive_stable} of {total} "
          f"({decisive_stable/total:.2f}); retained share of the per-seed "
          f"decisive words {decisive_stable/mean_dec:.2f}")
    print(f"- words with both pass and fail across seeds: {pass_fail_flip}")


def part3(text: str) -> None:
    print("\n## 3. Pairwise z for the primary parts (frozen systems)\n")
    zl = N.inv_cdf(1 - (1 - PRIMARY) / 2)
    rows = {}
    for line in section(text, "Primary intervals"):
        c = cells(line)
        if not c[0].startswith("ens-DEV"):
            continue
        seed, system, part = c[0][4:], c[1], c[2]
        est = float(c[3])
        lo, hi = (float(v) for v in re.findall(r"-?[\d.]+(?:e-?\d+)?", c[4]))
        rows[(system, part, seed)] = (est, lo, hi)
    parts = sorted({(s, p) for s, p, _ in rows})
    seeds = ("DEV-1", "DEV-3", "DEV-4")
    zs_sym, zs_away, n_part_pass_flip = [], [], 0
    print("| system | part | z_away 1-3 | 1-4 | 3-4 | max |")
    print("|---|---|---|---|---|---|")
    for system, part in parts:
        out = []
        for a, b in itertools.combinations(seeds, 2):
            e0, l0, h0 = rows[(system, part, a)]
            e1, l1, h1 = rows[(system, part, b)]
            d = e1 - e0
            hw0, hw1 = (h0 - l0) / 2, (h1 - l1) / 2
            arm0, arm1 = (e0 - l0, h1 - e1) if d > 0 else (h0 - e0, e1 - l1)
            z_sym = abs(d) / ((hw0 / zl) ** 2 + (hw1 / zl) ** 2) ** 0.5
            z_away = abs(d) / ((arm0 / zl) ** 2 + (arm1 / zl) ** 2) ** 0.5
            zs_sym.append(z_sym)
            zs_away.append(z_away)
            out.append(z_away)
        print(f"| {system} | {part} | " + " | ".join(f"{z:.2f}" for z in out)
              + f" | {max(out):.2f} |")
    n = len(zs_sym)
    m2 = sum(z * z for z in zs_sym) / n
    print(f"\n- pairs: {n}; mean z_sym^2 = {m2:.3f} (1 + tau^2/SE^2 under a "
          f"seed-dependent estimand; 1 under a fixed one; pairs share seeds, "
          f"so the effective count is about {n*2//3})")
    for c in (1.645, 1.96, 2.576, 3.4):
        k = sum(z > c for z in zs_away)
        print(f"- z_away > {c}: {k} of {n} (expected under a fixed estimand "
              f"and normal SEs: {n*2*(1-N.cdf(c)):.1f})")
    print(f"- max z_away {max(zs_away):.2f}, max z_sym {max(zs_sym):.2f}")


def part4() -> None:
    print("\n## 4. Power of the all-three rule\n")
    print("| per-seed pi | pi^3 (promoted) | 1 - sum pi_w^3 if the rest is "
          "inconclusive |")
    print("|---|---|---|")
    for pi in (0.5, 0.7, 0.8, 0.9, 0.95, 0.99):
        print(f"| {pi} | {pi**3:.3f} | {1 - pi**3 - (1-pi)**3:.3f} |")
    for z, lab in ((N.inv_cdf(1 - 0.05 / 6), "primary 98.3%"),
                   (N.inv_cdf(0.975), "secondary 95%")):
        one = z + N.inv_cdf(0.8)
        three = z + N.inv_cdf(0.8 ** (1 / 3))
        print(f"\n- {lab}: distance from the band edge for 80% power, in SE: "
              f"one seed {one:.3f}, all three {three:.3f}; ratio "
              f"{three/one:.3f}; equivalent one-seed sample-size factor "
              f"{(three/one)**2:.3f}")


def main() -> None:
    text = SRC.read_text()
    print("DEVELOPMENT (DEV-1, DEV-3, DEV-4): not a hypothesis test.\n")
    part1()
    part2(text)
    part3(text)
    part4()


if __name__ == "__main__":
    main()
