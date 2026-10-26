"""M-6 measurement of r on the exploration seeds (WU-0051b).

DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.

r is the between-seed SD of a row's point estimate over the three
exploration seeds, divided by the mean within-seed SE of that row (math spec
M-6). Within-seed SE: half the interval width over z at the row's level
(``z = Phi^-1(1 - (1 - level)/2)``); ratios on the log scale, differences
and retained shares on their own scale. Between-seed SD: sample SD (n = 3,
2 degrees of freedom). Two summaries are mapped to M-6's formulas:

* ``r_tot = SD / mean SE``, M-6's literal definition. The point estimates of
  different seeds also differ by their own sampling error, so plugging r_tot
  into ``p = Phi(-1.96 / sqrt(1 + r^2))`` counts the sampling part twice
  (conservative);
* ``r_omit = sqrt(max(r_tot^2 - 1, 0))``, the part the interval omits.

Families: allocation drop-one (MSE ratio), horizon drop-one (pinball ratio),
B Delta (allocation parts and horizon), D rungs against F (allocation MSE
ratio, horizon pinball ratio), C2 retained (forward, single-horizon,
reverse; L_A and L_w). A row enters if it exists on all three seeds with a
finite point and interval (and positive values on the log scale); every
exclusion is counted. "Unguarded" rows: no seed's reading is blocked by a
guard (n_eff, state count, failed resamples, full-profile skill).

Usage (CPU, a few seconds)::

    python -I r_measurement.py <runs/dev> <contrib dir name> <ce dir name>

with ``<runs/dev>/phj-DEV-{1,3,4}/<name>/{contrib,ce}.json``. Writes
``r_measurement.out.md`` beside this script.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import norm

SEEDS = ("DEV-1", "DEV-3", "DEV-4")
LABEL = "DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test"
GUARDED = ("n_eff", "n_states", "failed", "full-profile", "not computable")


def p_false(r: float) -> float:
    """M-6: per-seed false-claim probability with omitted SD r x SE."""
    return float(norm.cdf(-1.96 / math.sqrt(1.0 + r * r)))


def at_least(k: int, p: float, n: int = 5) -> float:
    """P(at least k of n) for independent seeds with probability p."""
    return float(
        sum(math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))
    )


def check_m6_table() -> None:
    """Reproduce the M-6 table (math spec, rounded as printed there)."""
    table = {0.8: (0.063, 7.5e-5), 1.0: (0.083, 2.2e-4), 1.5: (0.14, 1.6e-3),
             2.0: (0.19, 5.6e-3)}
    for r, (p, p4) in table.items():
        assert abs(p_false(r) - p) < 0.0051, (r, p_false(r))
        assert abs(at_least(4, p_false(r)) / p4 - 1) < 0.06, r


def guarded(row: dict) -> bool:
    reason = row.get("reason") or ""
    word = row.get("reading") or ""
    return any(g in reason for g in GUARDED) or (
        word.startswith("not determined (")
        and any(g in word for g in GUARDED)
    )


def rows_of(contrib: dict, ce: dict) -> dict[tuple, tuple[dict, str, str]]:
    """(family, id...) -> (row, value key, scale)."""
    out = {}
    for system, res in contrib["systems"].items():
        for h, kinds in res["allocation"].items():
            for kind, b in kinds.items():
                for x, row in b["drop_one"].items():
                    out[("allocation drop-one", system, h, kind, x)] = (
                        row["mse_ratio"], "ratio", "log")
                for rung, row in b["ladder"]["vs_full"].items():
                    out[("D rungs", system, "alloc", h, kind, rung)] = (
                        row["mse_ratio"], "ratio", "log")
        for h, kinds in res["interactions"].items():
            for kind, parts in kinds.items():
                for part, rec in parts.items():
                    for pair, row in rec.get("pairs", {}).items():
                        out[("B Delta", system, part, h, kind, pair)] = (
                            row, "difference", "linear")
        for kind, b in res["horizon"].items():
            for x, row in b["drop_one"].items():
                out[("horizon drop-one", system, kind, x)] = (
                    row["pinball_ratio"], "ratio", "log")
            for rung, row in b["ladder"]["vs_full"].items():
                out[("D rungs", system, "horizon", kind, rung)] = (
                    row["pinball_ratio"], "ratio", "log")
            for pair, row in b["interactions"]["pairs"].items():
                out[("B Delta", system, "log T", kind, pair)] = (
                    row, "difference", "linear")
    for system, res in ce["systems"].items():
        for kind in ("oracle", "deployable"):
            c2 = res["C2"][kind]
            for stat in ("retained", "retained_w"):
                out[("C2 retained", system, kind, "forward", stat)] = (
                    c2["forward"][stat], "ratio", "linear")
            for h, r in c2["forward"]["single_horizon"].items():
                out[("C2 retained", system, kind, "single", h)] = (
                    r["retained"], "ratio", "linear")
            for h, r in c2["reverse"].items():
                for stat in ("retained", "retained_w"):
                    out[("C2 retained", system, kind, "reverse", h, stat)] = (
                        r[stat], "ratio", "linear")
    return out


def row_r(rows: list[tuple[dict, str, str]]) -> tuple[dict | None, str]:
    """r of one row over the seeds, or None with the exclusion reason."""
    points, ses = [], []
    for row, key, scale in rows:
        value, (lo, hi) = row.get(key), row.get("ci", [None, None])
        if value is None or lo is None or hi is None:
            return None, "non-finite point or bound"
        if scale == "log":
            if min(value, lo, hi) <= 0:
                return None, "non-positive ratio"
            value, lo, hi = math.log(value), math.log(lo), math.log(hi)
        z = norm.ppf(1 - (1 - row["level"]) / 2)
        points.append(value)
        ses.append((hi - lo) / (2 * z))
    se = float(np.mean(ses))
    if se <= 0:
        return None, "zero interval width"
    sd = float(np.std(points, ddof=1))
    r_tot = sd / se
    return {
        "r_tot": r_tot,
        "r_omit": math.sqrt(max(r_tot**2 - 1.0, 0.0)),
        "guarded": any(guarded(row) for row, _, _ in rows),
        "sub": None,
    }, ""


def summary(values: list[float]) -> dict:
    v = np.array(values)
    return {
        "n": len(v),
        "median": float(np.median(v)),
        "q1": float(np.quantile(v, 0.25)),
        "q3": float(np.quantile(v, 0.75)),
        "rms": float(np.sqrt(np.mean(v**2))),
    }


def main(argv: list[str]) -> int:
    check_m6_table()
    base, abd_name, ce_name = Path(argv[0]), argv[1], argv[2]
    per_seed, commits = [], set()
    for seed in SEEDS:
        folder = base / f"phj-{seed}"
        contrib = json.loads((folder / abd_name / "contrib.json").read_text())
        ce = json.loads((folder / ce_name / "ce.json").read_text())
        assert contrib["run"]["seed_id"] == ce["run"]["seed_id"] == seed
        commits |= {contrib["analysis"]["commit"], ce["analysis"]["commit"]}
        per_seed.append(rows_of(contrib, ce))
    keys = sorted(set().union(*per_seed))
    results: dict[str, list[dict]] = defaultdict(list)
    excluded: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for key in keys:
        family = key[0]
        if any(key not in s for s in per_seed):
            excluded[family]["absent on a seed"] += 1
            continue
        res, why = row_r([s[key] for s in per_seed])
        if res is None:
            excluded[family][why] += 1
            continue
        if family == "B Delta":
            res["sub"] = "horizon (log T)" if key[2] == "log T" else (
                "allocation logit" if key[2] == "logit"
                else "allocation zero/one/decision")
        results[family].append(res)
    lines = [
        "# r measurement (M-6): output of r_measurement.py",
        "",
        f"**{LABEL}.** Analysis commit(s): "
        + ", ".join(f"`{c}`" for c in sorted(commits))
        + f". Inputs: `{base}/phj-DEV-n/{abd_name}`, `{ce_name}`.",
        "",
        "p = Phi(-1.96/sqrt(1+r^2)); P4 = P(at least 4 of 5); P3 = P(at "
        "least 3 of 5); E1000 = expected false replications per 1000 null "
        "rows at P4. M-6 table reproduced by `check_m6_table` (passed).",
        "",
    ]
    head = (
        "| family | subset | rows | excluded | r_tot median [Q1, Q3] | r_tot "
        "RMS | r_omit median [Q1, Q3] | r_omit RMS |"
    )
    lines += [f"{LABEL}.", "", head, "|---|---|---|---|---|---|---|---|"]
    mapping = []
    order = ("allocation drop-one", "horizon drop-one", "B Delta", "D rungs",
             "C2 retained")
    for family in order:
        rs = results[family]
        subsets = [("all", rs), ("unguarded", [r for r in rs
                                               if not r["guarded"]])]
        if family == "B Delta":
            for name in ("allocation logit", "allocation zero/one/decision",
                         "horizon (log T)"):
                subsets.append((name, [r for r in rs if r["sub"] == name]))
        for name, sel in subsets:
            if not sel:
                lines.append(f"| {family} | {name} | 0 | | | | | |")
                continue
            t = summary([r["r_tot"] for r in sel])
            o = summary([r["r_omit"] for r in sel])
            ex = "; ".join(f"{k} {v}" for k, v in excluded[family].items())
            lines.append(
                f"| {family} | {name} | {t['n']} | "
                f"{ex if name == 'all' else ''} | {t['median']:.2f} "
                f"[{t['q1']:.2f}, {t['q3']:.2f}] | {t['rms']:.2f} | "
                f"{o['median']:.2f} [{o['q1']:.2f}, {o['q3']:.2f}] | "
                f"{o['rms']:.2f} |"
            )
            if name == "all":
                mapping.append((family, t, o))
    lines += [
        "",
        f"{LABEL}.",
        "",
        "| family | r used | r | p | P4 | P3 | E1000 |",
        "|---|---|---|---|---|---|---|",
    ]
    for family, t, o in mapping:
        for label, r in (("r_tot median", t["median"]), ("r_tot Q3", t["q3"]),
                         ("r_tot RMS", t["rms"]), ("r_omit median",
                                                    o["median"]),
                         ("r_omit RMS", o["rms"])):
            p = p_false(r)
            p4, p3 = at_least(4, p), at_least(3, p)
            lines.append(
                f"| {family} | {label} | {r:.2f} | {p:.3f} | {p4:.1e} | "
                f"{p3:.1e} | {1000 * p4:.2f} |"
            )
    chi_lo, chi_hi = (float(np.sqrt(2 / q)) for q in _chi2_quantiles())
    lines += [
        "",
        f"With 2 degrees of freedom, the true SD of a row lies between "
        f"{chi_lo:.2f} and {chi_hi:.2f} times its estimate (95%); for a common r "
        f"the median of the per-row ratios is biased low by a factor "
        f"{math.sqrt(math.log(2)):.3f} (median of sqrt(chi2_2 / 2)), while "
        "the RMS estimates r^2 without that bias.",
        "",
    ]
    out = Path(__file__).with_name("r_measurement.out.md")
    out.write_text("\n".join(lines))
    print(out)
    return 0


def _chi2_quantiles() -> tuple[float, float]:
    """chi2_2 quantiles 0.975 and 0.025 (closed form: -2 ln(1 - q))."""
    return -2 * math.log(0.025), -2 * math.log(0.975)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
