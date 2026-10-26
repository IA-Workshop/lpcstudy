#!/usr/bin/env python3
"""Phase J replication rule M-6, applied mechanically (WU-0051b).

DEVELOPMENT: phase J replication (held-out development seeds), not a
hypothesis test. The tool reads, for each of N seeds, the A/B/D record
``contrib.json`` (``tools/lpc_contrib.py``) and the C/E record ``ce.json``
(``tools/lpc_contrib_ce.py``) of one analysis commit, lines up every reading
row across the seeds, and classifies each row by the rule of the math spec
(``docs/agent/notes/2026-10-26-phase-j-math-spec.md``, M-6):

* **contradicted**: some pair of seeds has jointly unsatisfiable bound
  claims (the plan's "seed-dependent");
* **replicated**: otherwise, if one claim-bearing reading occurs on at least
  4 of the 5 seeds;
* **not replicated**: otherwise (typically imprecision).

For a row that is not replicated, the claim-level fallback reports every
atomic bound claim (for example ``ratio > 1``) that at least 4 seeds' claims
imply and no seed's claims contradict, as a "replicated claim".

Claims
    Every reading word maps to a conjunction of claims ``quantity op value``
    on the true value of the row's quantity (:func:`claims_of`), derived from
    the rule that produced the word. Two readings contradict iff the union of
    their claims is unsatisfiable (:func:`satisfiable`). A word with no claim
    ("undetermined", "not determined (...)", "not identifiable", and the
    non-detections "no interaction gain detected", "no difference detected",
    "no detectable dependence bias", "realized-noise outlier, no detectable
    dependence bias") never contradicts and never counts toward the minimum.
    :data:`VOCABULARY` lists every word with its claim template; a word that
    is not in it, or a ``reading`` leaf that no row covers, is refused, so a
    change of the analysis cannot drop a row silently.

Usage::

    python tools/lpc_replicate.py <dir> <dir> ... --out <dir> [--exploratory]

Each ``<dir>`` holds one seed's ``contrib.json`` and ``ce.json``. Writes
``replication.json`` and ``replication.md``.

Refusals (exit 64, nothing written): an argument containing "confirmatory"
or "CONF-" (any case); a record whose text contains either; a seed id that is
not ``DEV-n``; records of different analysis commits (contrib and ce, every
seed) or of different presets; a C/E record of another seed or run, or
without its A/D record; an unknown reading word or an uncovered reading leaf.
Without ``--exploratory`` also: N other than 5, a seed set other than the
held-out DEV-5 to DEV-9, a record with uncommitted analysis code. With
``--exploratory`` any N >= 2 runs, the minimum is ``ceil(4 N / 5)``, repeated
seeds are allowed and counted, and the output is labeled as not the rule.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import lpc_contrib as base  # noqa: E402
from lpcstudy.ablation import RATIO_MARGIN  # noqa: E402
from lpcstudy.contribution import NO_GAIN  # noqa: E402
from lpcstudy.joint_decisions import RETAIN_LEVEL  # noqa: E402
from lpcstudy.mechanisms import (  # noqa: E402
    HEAVY_TAIL,
    LIGHT_TAIL,
    NEAR_ZERO,
    UNIMODAL_BC,
)

Refusal = base.Refusal
LABEL = (
    "DEVELOPMENT: phase J replication (held-out development seeds), "
    "not a hypothesis test"
)
HELD_OUT = tuple(f"DEV-{k}" for k in range(5, 10))
"""The replication seeds of phase J (plan DV-4, section 10)."""
RULE_SEEDS = 5
RULE_MINIMUM = 4
SYSTEMS = ("lorenz63", "rossler", "chua")
PAIR_NAMES = ("RO", "RI", "RN", "OI", "ON", "IN")
"""B's six pairs, in ``contribution.PAIRS`` order."""
FORBIDDEN = re.compile(r"confirmatory|conf-", re.IGNORECASE)


# ------------------------------------------------------------------ claims
@dataclass(frozen=True)
class Claim:
    """``quantity op value`` on the true value of a row's quantity.

    ``basis`` says what established it in the seed: ``interval`` (a bound of
    the row's interval), ``test`` (a Holm-adjusted one-sided test) or
    ``point`` (a point estimate against a threshold, E-H2a drift, E-H3c).
    """

    quantity: str
    op: str
    value: float
    basis: str = "interval"

    def text(self) -> str:
        return f"{self.quantity} {self.op} {self.value:g}"


NEGATION = {"<": ">=", "<=": ">", ">": "<=", ">=": "<"}


def satisfiable(claims) -> bool:
    """True if some value of every quantity meets all the claims on it."""
    by_quantity: dict[str, list[Claim]] = defaultdict(list)
    for claim in claims:
        by_quantity[claim.quantity].append(claim)
    for group in by_quantity.values():
        low, low_open = -math.inf, True
        high, high_open = math.inf, True
        for c in group:
            strict = c.op in ("<", ">")
            if c.op in (">", ">="):
                if c.value > low or (c.value == low and strict):
                    low, low_open = c.value, strict
            elif c.value < high or (c.value == high and strict):
                high, high_open = c.value, strict
        if low > high or (low == high and (low_open or high_open)):
            return False
    return True


def contradict(first, second) -> bool:
    """Two claim sets contradict iff their union is unsatisfiable."""
    return not satisfiable((*first, *second))


def implies(claims, claim: Claim) -> bool:
    """``claims`` imply ``claim`` iff ``claims`` and its negation clash."""
    negation = Claim(claim.quantity, NEGATION[claim.op], claim.value)
    return not satisfiable((*claims, negation))


# -------------------------------------------------------------- vocabulary
def _c(quantity: str, op: str, value: float, basis: str = "interval"):
    return Claim(quantity, op, float(value), basis)


RATIO = {
    "lowers": (_c("ratio", "<", 1),),
    "negligible": (_c("ratio", "<=", RATIO_MARGIN),),
    "small": (_c("ratio", ">", 1), _c("ratio", "<=", RATIO_MARGIN)),
    "substantial": (_c("ratio", ">", RATIO_MARGIN),),
    "needed, size not determined": (_c("ratio", ">", 1),),
    "undetermined": (),
    "not identifiable": (),
    NO_GAIN: (_c("ratio", "<", 1),),
}
"""The 1.05 table (``ablation.ratio_reading``): bound claims on the ratio.

``NO_GAIN`` replaces "lowers" on a B loss-ratio row (addendum R1): the same
claim, ``ratio < 1``.
"""
PAIR = {
    "interaction gain detected": (_c("delta", ">", 0, "test"),),
    "no interaction gain detected": (),
    NO_GAIN: (_c("delta", "<", 0),),
}
"""B's pair rows: Delta = L(additive) - L(additive + pair)."""
RETAINED = {
    "keeps most": (_c("retained", ">", RETAIN_LEVEL),),
    "loses most": (_c("retained", "<", RETAIN_LEVEL),),
}
"""C2's retained skill; every "not determined (...)" word carries none."""
RETAINED_DIFFERENCE = {
    "deployable retains less": (_c("difference", "<", 0),),
    "deployable retains more": (_c("difference", ">", 0),),
    "no difference detected": (),
}
"""C2 oracle against deployable: retained(deployable) - retained(oracle)."""
BIAS_NONE = (
    "no detectable dependence bias",
    "realized-noise outlier, no detectable dependence bias",
)
BIAS_DETECTED = "dependence bias detectable (interval excludes 0)"
E_WORDS = ("consistent", "not consistent")

VOCABULARY: dict[str, dict[str, str]] = {
    "ratio (1.05 table)": {
        w: " and ".join(c.text() for c in cs) or "none"
        for w, cs in RATIO.items()
    },
    "B pair (Delta, Holm)": {
        w: " and ".join(c.text() for c in cs) or "none"
        for w, cs in PAIR.items()
    },
    "C2 retained": {
        **{w: cs[0].text() for w, cs in RETAINED.items()},
        "not determined (...)": "none",
    },
    "C2 oracle vs deployable": {
        **{
            w: " and ".join(c.text() for c in cs) or "none"
            for w, cs in RETAINED_DIFFERENCE.items()
        },
        "not determined (...)": "none",
    },
    "C2 prediction (both lose most)": {
        "consistent": f"forward retained < {RETAIN_LEVEL:g}, and reverse@H "
        f"retained < {RETAIN_LEVEL:g} at every H whose reading is determined",
        "not consistent": f"retained > {RETAIN_LEVEL:g} on every component "
        "reading 'keeps most'",
        "not determined": "none",
    },
    "check (f2) dependence bias": {
        **{w: "none" for w in BIAS_NONE},
        BIAS_DETECTED: "bias > 0 or bias < 0, the side of the interval",
    },
    "E-H2a": {
        "consistent": "at every supporting H: Spearman(m, I)@H > 0 or < 0 "
        "(the side of its interval), and drift(high I) - drift(low I)@H > 0 "
        "(point)",
        "not consistent": f"at every usable H: -{NEAR_ZERO:g} < Spearman(m, "
        f"I)@H < {NEAR_ZERO:g}",
        "not determined (...)": "none",
    },
    "E-H2e part": {
        "consistent": "median Delta corr > 0 and Spearman(Delta corr, Delta "
        "R) < 0",
        "not consistent": "Spearman > 0 and/or median < 0, whichever interval "
        "established it",
        "not determined": "none",
    },
    "E-H2e level (final)": {
        "consistent / not consistent": "the claims of both parts (all, "
        "both_defined), which agree",
        "not determined (...)": "none",
    },
    "E-H3c Lorenz-63 part (point)": {
        "consistent": f"top-1% share >= {HEAVY_TAIL:g} and median I "
        "percentile >= 2/3",
        "not consistent": f"top-1% share < {LIGHT_TAIL:g} and/or median I "
        "percentile < 1/2, whichever holds",
        "not determined": "none",
    },
    "E-H3c Rossler part (point)": {
        "consistent": f"BC < {UNIMODAL_BC:.4g} for R, O, I and N",
        "not consistent": f"BC > {UNIMODAL_BC:.4g} for each coordinate where "
        "it holds (two or more)",
        "not determined": "none",
    },
    "E-H3c overall (point)": {
        "consistent": "width ordering (Lorenz-63 widest, Rossler narrowest) "
        "and both parts' consistent claims",
        "not consistent": "width ordering and the claims of each part that "
        "reads not consistent",
        "not determined (...)": "none",
    },
}
"""Every reading word the tools emit, with its claims (documentation)."""


def ratio_claims(word: str, path: str) -> tuple[Claim, ...]:
    if word not in RATIO:
        raise Refusal(f"unknown ratio reading {word!r} at {path}")
    return RATIO[word]


def table_claims(table: dict, word: str, path: str) -> tuple[Claim, ...]:
    """Claims of a word of a C2 table; any "not determined (...)" has none."""
    if word in table:
        return table[word]
    if word == "not determined" or word.startswith("not determined ("):
        return ()
    raise Refusal(f"unknown reading {word!r} at {path}")


def _side(ci: list, quantity: str, basis: str = "interval") -> tuple:
    """The claim an interval that excludes 0 makes (``()`` if it does not)."""
    lower, upper = ci
    if lower is not None and lower > 0:
        return (_c(quantity, ">", 0, basis),)
    if upper is not None and upper < 0:
        return (_c(quantity, "<", 0, basis),)
    return ()


def bias_claims(row: dict, path: str) -> tuple[Claim, ...]:
    word = row["reading"]
    if word in BIAS_NONE:
        return ()
    if word != BIAS_DETECTED:
        raise Refusal(f"unknown dependence-bias reading {word!r} at {path}")
    claims = _side(row["dependence"]["ci"], "bias")
    if not claims:
        raise Refusal(f"{path}: 'detectable' but the interval spans 0")
    return claims


def h2a_claims(block: dict, path: str) -> tuple[Claim, ...]:
    """E-H2a (``mechanisms.h2a_reading``)."""
    rec = block["reading"]
    word = rec["reading"]
    if word == "consistent":
        out = []
        for h in rec["horizons_supporting"]:
            row = block["by_horizon"][h]
            side = _side(row["spearman_m_I"]["ci"], f"Spearman(m, I)@{h}")
            if not side:
                raise Refusal(f"{path}: supporting H={h} spans 0")
            out += [*side, _c(f"drift high - low I@{h}", ">", 0, "point")]
        return tuple(out)
    if word == "not consistent":
        return tuple(
            c
            for h in rec["horizons_used"]
            for c in (
                _c(f"Spearman(m, I)@{h}", ">", -NEAR_ZERO),
                _c(f"Spearman(m, I)@{h}", "<", NEAR_ZERO),
            )
        )
    return table_claims({}, word, path)


def h2e_part_claims(part: dict, path: str) -> tuple[Claim, ...]:
    """E-H2e, one state set (``mechanisms.h2e_part_reading``)."""
    word = part["reading"]
    median = part["median_delta_corr"]["ci"]
    spearman = part["spearman_delta_corr_delta_R"]["ci"]
    if word == "consistent":
        return (
            _c("median Delta corr", ">", 0),
            _c("Spearman(Delta corr, Delta R)", "<", 0),
        )
    if word == "not consistent":
        out = []
        if spearman[0] is not None and spearman[0] > 0:
            out.append(_c("Spearman(Delta corr, Delta R)", ">", 0))
        if median[1] is not None and median[1] < 0:
            out.append(_c("median Delta corr", "<", 0))
        if not out:
            raise Refusal(f"{path}: 'not consistent' without its bound")
        return tuple(out)
    return table_claims({}, word, path)


def h2e_level_claims(level: dict, path: str) -> tuple[Claim, ...]:
    """The final E-H2e reading: both parts' claims when they agree."""
    word = level["reading"]
    if word in E_WORDS:
        return tuple(
            Claim(f"{name}: {c.quantity}", c.op, c.value, c.basis)
            for name, part in level["parts"].items()
            for c in h2e_part_claims(part, f"{path}/parts/{name}")
        )
    return table_claims({}, word, path)


def h3c_lorenz_claims(rec: dict, word: str) -> tuple[Claim, ...]:
    share = rec["lorenz63_tail_share"]
    pct = rec["lorenz63_top_median_I_percentile"]
    if word == "consistent":
        return (
            _c("Lorenz-63 top-1% share", ">=", HEAVY_TAIL, "point"),
            _c("Lorenz-63 top median I pct", ">=", 2.0 / 3.0, "point"),
        )
    if word == "not consistent":
        out = []
        if share < LIGHT_TAIL:
            out.append(_c("Lorenz-63 top-1% share", "<", LIGHT_TAIL, "point"))
        if pct < 0.5:
            out.append(_c("Lorenz-63 top median I pct", "<", 0.5, "point"))
        return tuple(out)
    return table_claims({}, word, "E_H3c_reading/lorenz63_part")


def h3c_rossler_claims(rec: dict, word: str) -> tuple[Claim, ...]:
    bc = rec["rossler_bimodality"]
    if word == "consistent":
        return tuple(
            _c(f"Rossler BC {x}", "<", UNIMODAL_BC, "point") for x in bc
        )
    if word == "not consistent":
        return tuple(
            _c(f"Rossler BC {x}", ">", UNIMODAL_BC, "point")
            for x, v in bc.items()
            if v > UNIMODAL_BC
        )
    return table_claims({}, word, "E_H3c_reading/rossler_part")


def h3c_claims(rec: dict) -> tuple[Claim, ...]:
    """E-H3c overall (``mechanisms.h3c_reading``)."""
    word = rec["reading"]
    if word not in E_WORDS:
        return table_claims({}, word, "E_H3c_reading")
    pattern = (
        _c("width lorenz63 - chua", ">=", 0, "point"),
        _c("width lorenz63 - rossler", ">=", 0, "point"),
        _c("width chua - rossler", ">=", 0, "point"),
    )
    parts = (
        (rec["lorenz63_part"], h3c_lorenz_claims),
        (rec["rossler_part"], h3c_rossler_claims),
    )
    if word == "consistent":
        return pattern + tuple(c for p, f in parts for c in f(rec, p))
    return pattern + tuple(
        c for p, f in parts if p == "not consistent" for c in f(rec, p)
    )


def prediction_claims(c2: dict, path: str) -> tuple[Claim, ...]:
    """C2 prediction check (``joint_decisions.c2_prediction``)."""
    word = c2["prediction_check"]["reading"]
    rows = {"forward": c2["forward"]["retained"]["reading"]} | {
        f"reverse@{h}": r["retained"]["reading"]
        for h, r in c2["reverse"].items()
    }
    if word == "consistent":
        return tuple(
            _c(f"{k} retained", "<", RETAIN_LEVEL)
            for k, w in rows.items()
            if w in RETAINED
        )
    if word == "not consistent":
        return tuple(
            _c(f"{k} retained", ">", RETAIN_LEVEL)
            for k, w in rows.items()
            if w == "keeps most"
        )
    return table_claims({}, word, path)


# ---------------------------------------------------------------- the rows
@dataclass(frozen=True)
class Reading:
    """One seed's reading of one row."""

    word: str
    claims: tuple[Claim, ...]
    path: str


ROW_FIELDS = ("system", "family", "decision", "profile", "horizon", "item")


class Rows:
    """The reading rows of one seed, keyed by their identity."""

    def __init__(self) -> None:
        self.rows: dict[tuple, Reading] = {}

    def add(self, key: tuple, word: str, claims, path: str) -> None:
        if key in self.rows:
            raise Refusal(f"row {key} appears twice ({path})")
        self.rows[key] = Reading(word, tuple(claims), path)

    def ratio(self, key: tuple, row: dict, path: str) -> None:
        word = row["reading"]
        self.add(key, word, ratio_claims(word, path), path)


def contrib_rows(record: dict, rows: Rows) -> None:
    """Every reading row of an A/B/D record (``contrib.json``)."""
    for system, res in record["systems"].items():
        root = f"contrib/systems/{system}"
        for hkey, blocks in res["allocation"].items():
            for kind, b in blocks.items():
                h, p = b["horizon"], f"{root}/allocation/{hkey}/{kind}"
                key = (system, "", "allocation", kind, h)
                for x, row in b["drop_one"].items():
                    rows.ratio(
                        _k(key, "A drop-one", f"drop {x}: MSE ratio"),
                        row["mse_ratio"],
                        f"{p}/drop_one/{x}/mse_ratio/reading",
                    )
                for name, sub in b["subsets"].items():
                    if "reading" in sub.get("mse_vs_separation", {}):
                        rows.ratio(
                            _k(key, "A vs separation",
                               f"{name}: MSE(F)/MSE(sep)"),
                            sub["mse_vs_separation"],
                            f"{p}/subsets/{name}/mse_vs_separation/reading",
                        )
                _ladder(rows, key, b["ladder"], "mse_ratio", f"{p}/ladder")
                for rule, d in b.get("dependence_bias", {}).items():
                    q = f"{p}/dependence_bias/{rule}/reading"
                    rows.add(
                        _k(key, "check (f2)", f"{rule}: dependence bias"),
                        d["reading"],
                        bias_claims(d, q),
                        q,
                    )
        for hkey, kinds in res["interactions"].items():
            for kind, parts in kinds.items():
                h = res["allocation"][hkey][kind]["horizon"]
                for part, rec in parts.items():
                    p = f"{root}/interactions/{hkey}/{kind}/{part}"
                    key = (system, "", "allocation", kind, h)
                    _pairs(rows, key, part, rec, p)
        for kind, b in res["horizon"].items():
            p = f"{root}/horizon/{kind}"
            key = (system, "", "horizon", kind, "T_c")
            for x, row in b["drop_one"].items():
                rows.ratio(
                    _k(key, "A drop-one", f"drop {x}: pinball ratio"),
                    row["pinball_ratio"],
                    f"{p}/drop_one/{x}/pinball_ratio/reading",
                )
            _ladder(rows, key, b["ladder"], "pinball_ratio", f"{p}/ladder")
            _pairs(rows, key, "log T", b["interactions"], f"{p}/interactions")


def _k(key: tuple, family: str, item: str) -> tuple:
    """``(system, family, decision, profile, horizon, item)``."""
    return (key[0], family, *key[2:5], item)


def _ladder(rows: Rows, key: tuple, ladder: dict, stat: str, p: str) -> None:
    for rung, row in ladder["vs_full"].items():
        rows.ratio(
            _k(key, "D vs full", f"{rung}: {stat.replace('_', ' ')} vs F"),
            row[stat],
            f"{p}/vs_full/{rung}/{stat}/reading",
        )
    for step, row in ladder["vs_below"].items():
        rows.ratio(
            _k(key, "D vs below", f"{step}"),
            row,
            f"{p}/vs_below/{step}/reading",
        )


def _pairs(rows: Rows, key: tuple, part: str, rec: dict, p: str) -> None:
    """B: six pair rows and six loss-ratio rows of one part.

    A part without pairs (a single-class training set) reads "undetermined";
    its twelve rows get that word, which carries no claim.
    """
    for name in PAIR_NAMES:
        k_pair = _k(key, "B pair", f"{part} {name}: Delta")
        k_ratio = _k(key, "B loss ratio", f"{part} {name}: L(add)/L(pair)")
        if "pairs" not in rec:
            word = rec["reading"]
            if ratio_claims(word, f"{p}/reading"):
                raise Refusal(f"{p}: part-level reading {word!r} has claims")
            rows.add(k_pair, word, (), f"{p}/reading")
            rows.add(k_ratio, word, (), f"{p}/reading")
            continue
        row = rec["pairs"][name]
        q = f"{p}/pairs/{name}"
        if row["reading"] not in PAIR:
            raise Refusal(f"unknown pair reading {row['reading']!r} at {q}")
        rows.add(k_pair, row["reading"], PAIR[row["reading"]], f"{q}/reading")
        rows.ratio(k_ratio, row["loss_ratio"], f"{q}/loss_ratio/reading")


def ce_rows(record: dict, rows: Rows) -> None:
    """Every reading row of a C/E record (``ce.json``)."""
    for system, res in record["systems"].items():
        root = f"ce/systems/{system}"
        c1 = res.get("C1", {})
        for hkey, kinds in c1.get("allocation", {}).items():
            for kind, b in kinds.items():
                key = (system, "", "allocation", kind, b["horizon"])
                for rung, word in b["reading_vs_F"].items():
                    q = (f"{root}/C1/allocation/{hkey}/{kind}/"
                         f"reading_vs_F/{rung}")
                    rows.add(
                        _k(key, "C1", f"{rung}: MSE ratio vs F"),
                        word,
                        ratio_claims(word, q),
                        q,
                    )
        for kind, rungs in c1.get("horizon", {}).items():
            key = (system, "", "horizon", kind, "T_c")
            for rung, r in rungs.items():
                word = r.get("reading_vs_F") if isinstance(r, dict) else None
                if word is None:
                    continue
                q = f"{root}/C1/horizon/{kind}/{rung}/reading_vs_F"
                rows.add(
                    _k(key, "C1", f"{rung}: pinball ratio vs F"),
                    word,
                    ratio_claims(word, q),
                    q,
                )
        _c2_rows(rows, system, res["C2"], f"{root}/C2")
        _c3_rows(rows, system, res["C3"], f"{root}/C3")
        p = f"{root}/E_H2a/reading/reading"
        rows.add(
            (system, "E-H2a", "mechanism", "oracle", "all", "reading"),
            res["E_H2a"]["reading"]["reading"],
            h2a_claims(res["E_H2a"], p),
            p,
        )
        for rho, level in res["E_H2e"]["levels"].items():
            p = f"{root}/E_H2e/levels/{rho}"
            key = (system, "E-H2e", "mechanism", "oracle", f"rho {rho}")
            for name, part in level["parts"].items():
                q = f"{p}/parts/{name}/reading"
                rows.add(
                    (*key, f"part {name}"),
                    part["reading"],
                    h2e_part_claims(part, q),
                    q,
                )
            rows.add(
                (*key, "final"),
                level["reading"],
                h2e_level_claims(level, f"{p}/reading"),
                f"{p}/reading",
            )
    rec = record.get("E_H3c_reading")
    if rec is not None:
        key = ("all", "E-H3c", "mechanism", "deployable", "H_ref")
        rows.add(
            (*key, "overall"),
            rec["reading"],
            h3c_claims(rec),
            "ce/E_H3c_reading/reading",
        )
        for part, f in (
            ("lorenz63_part", h3c_lorenz_claims),
            ("rossler_part", h3c_rossler_claims),
        ):
            rows.add(
                (*key, part),
                rec[part],
                f(rec, rec[part]),
                f"ce/E_H3c_reading/{part}",
            )


def _c2_rows(rows: Rows, system: str, c2: dict, root: str) -> None:
    for kind in ("oracle", "deployable"):
        if kind not in c2:
            continue
        b, p = c2[kind], f"{root}/{kind}"
        fwd = b["forward"]
        key = (system, "", "joint", kind, "all five")
        for stat in ("retained", "retained_w"):
            _retained(rows, _k(key, "C2 retained", f"forward {stat}"),
                      fwd[stat], f"{p}/forward/{stat}/reading")
        for stat in (
            "pinball_ratio_bottleneck_over_F",
            "pinball_ratio_bottleneck_over_F_w",
        ):
            if stat in fwd:
                rows.ratio(_k(key, "C2 ratio", f"forward {stat}"), fwd[stat],
                           f"{p}/forward/{stat}/reading")
        for h, r in fwd["single_horizon"].items():
            _retained(
                rows,
                _k((system, "", "joint", kind, r["horizon"]), "C2 retained",
                   "forward one weight retained"),
                r["retained"],
                f"{p}/forward/single_horizon/{h}/retained/reading",
            )
        for h, r in b["reverse"].items():
            key_h = (system, "", "joint", kind, r["horizon"])
            for stat in ("retained", "retained_w"):
                _retained(rows, _k(key_h, "C2 retained", f"reverse {stat}"),
                          r[stat], f"{p}/reverse/{h}/{stat}/reading")
            rows.ratio(
                _k(key_h, "C2 ratio", "reverse MSE(h)/MSE(F)"),
                r["mse_ratio_bottleneck_over_F"],
                f"{p}/reverse/{h}/mse_ratio_bottleneck_over_F/reading",
            )
        q = f"{p}/prediction_check/reading"
        rows.add(
            _k(key, "C2 prediction", "both lose most"),
            b["prediction_check"]["reading"],
            prediction_claims(b, q),
            q,
        )
    for name, r in c2.get("oracle_vs_deployable", {}).items():
        q = f"{root}/oracle_vs_deployable/{name}/reading"
        rows.add(
            (system, "C2 oracle vs deployable", "joint", "both", name,
             "retained difference"),
            r["reading"],
            table_claims(RETAINED_DIFFERENCE, r["reading"], q),
            q,
        )


def _retained(rows: Rows, key: tuple, row: dict, path: str) -> None:
    rows.add(key, row["reading"],
             table_claims(RETAINED, row["reading"], path), path)


def _c3_rows(rows: Rows, system: str, c3: dict, root: str) -> None:
    for name, pol in c3["policies"].items():
        for h, m in pol["mse"].items():
            if "reading" in m.get("ratio_to_A2", {}):
                rows.ratio(
                    (system, "C3 ratio", "joint", "deployable", m["horizon"],
                     f"{name}: MSE ratio to A2"),
                    m["ratio_to_A2"],
                    f"{root}/policies/{name}/mse/{h}/ratio_to_A2/reading",
                )
    for name, r in c3["horizon_models"].items():
        rows.ratio(
            (system, "C3 ratio", "joint", "deployable", "T_c",
             f"{name}: pinball constant/model"),
            r["pinball_ratio_constant_over_model"],
            f"{root}/horizon_models/{name}/"
            "pinball_ratio_constant_over_model/reading",
        )


def reading_leaves(value, path: str) -> set[str]:
    """Paths of every string leaf under a key ``reading`` (completeness)."""
    found: set[str] = set()
    if isinstance(value, dict):
        for k, v in value.items():
            if k == "reading" and isinstance(v, str):
                found.add(f"{path}/{k}")
            found |= reading_leaves(v, f"{path}/{k}")
    elif isinstance(value, list):
        for v in value:
            found |= reading_leaves(v, path)
    return found


def seed_rows(contrib: dict, ce: dict) -> dict[tuple, Reading]:
    """Every reading row of one seed; refuse a ``reading`` leaf left over."""
    rows = Rows()
    contrib_rows(contrib, rows)
    ce_rows(ce, rows)
    covered = {r.path for r in rows.rows.values()}
    leaves = reading_leaves(contrib, "contrib") | reading_leaves(ce, "ce")
    missing = sorted(leaves - covered)
    if missing:
        raise Refusal(
            f"{len(missing)} reading leaves not covered, e.g. {missing[0]}"
        )
    return rows.rows


# ---------------------------------------------------------------- the rule
def atomic(claims) -> list[Claim]:
    """The distinct single claims (fallback candidates), basis dropped."""
    seen = {}
    for c in claims:
        seen.setdefault((c.quantity, c.op, c.value), c)
    return list(seen.values())


def classify(readings: list[Reading | None], minimum: int) -> dict:
    """The M-6 class of one row from its seeds' readings (``None``: absent).

    Contradicted if any pair of present readings has unsatisfiable claims;
    else replicated if one claim-bearing word occurs at least ``minimum``
    times; else not replicated. Rows that are not replicated get the
    claim-level fallback: each atomic claim of any seed that at least
    ``minimum`` seeds imply and no seed contradicts (claims implied by a
    stronger replicated claim on the same quantity are dropped).
    """
    present = [(i, r) for i, r in enumerate(readings) if r is not None]
    pairs = [
        [i, a.word, j, b.word]
        for n, (i, a) in enumerate(present)
        for j, b in present[n + 1 :]
        if contradict(a.claims, b.claims)
    ]
    bearing = Counter(r.word for _, r in present if r.claims)
    word, count = (bearing.most_common(1) or [(None, 0)])[0]
    out = {
        "class": "not replicated",
        "replicated_reading": None,
        "modal_claim_word": word,
        "modal_count": count,
        "n_claim_free": sum(1 for _, r in present if not r.claims),
        "n_absent": len(readings) - len(present),
        "contradicting_pairs": pairs,
        "replicated_claims": [],
    }
    if pairs:
        out["class"] = "contradicted"
    elif count >= minimum:
        out["class"] = "replicated"
        out["replicated_reading"] = word
        return out
    passing = []
    for claim in atomic(c for _, r in present for c in r.claims):
        holds = sum(1 for _, r in present if implies(r.claims, claim))
        clash = any(contradict(r.claims, (claim,)) for _, r in present)
        if holds >= minimum and not clash:
            passing.append(claim)
    out["replicated_claims"] = [
        c.text()
        for c in passing
        if not any(
            o is not c and implies((o,), c) and not implies((c,), o)
            for o in passing
        )
    ]
    return out


# ----------------------------------------------------------------- checks
def check_records(records: list[dict], exploratory: bool) -> dict:
    """The refusals of the module docstring; the run's metadata."""
    n = len(records)
    seeds = []
    for rec in records:
        contrib, ce = rec["contrib"], rec["ce"]
        seed = str(contrib["run"]["seed_id"])
        if not re.fullmatch(r"DEV-\d+", seed):
            raise Refusal(f"{rec['dir']}: not a development seed: {seed!r}")
        same = ce["run"]["dir"] == contrib["run"]["dir"]
        if ce["run"]["seed_id"] != seed or not same:
            raise Refusal(f"{rec['dir']}: ce.json of another run")
        if not ce.get("abd"):
            raise Refusal(f"{rec['dir']}: ce.json without its A/D record")
        if ce["abd"]["commit"] != contrib["analysis"]["commit"]:
            raise Refusal(f"{rec['dir']}: ce.json read another A/D commit")
        seeds.append(seed)
    commits = {
        r[k]["analysis"]["commit"] for r in records for k in ("contrib", "ce")
    }
    if len(commits) != 1:
        raise Refusal(f"different analysis commits: {sorted(commits)}")
    presets = {r["contrib"]["run"].get("preset") for r in records}
    if len(presets) != 1:
        raise Refusal(f"runs of different presets: {sorted(map(str, presets))}")
    dirty = any(
        r[k]["analysis"]["dirty"] for r in records for k in ("contrib", "ce")
    )
    repeated = n - len(set(seeds))
    if exploratory:
        if n < 2:
            raise Refusal("at least two seeds are needed")
        minimum = math.ceil(RULE_MINIMUM * n / RULE_SEEDS)
        label = (
            f"DEVELOPMENT ({', '.join(dict.fromkeys(seeds))}): EXPLORATORY "
            f"replication count (--exploratory: N = {n}, at least {minimum} "
            f"of {n}), not the M-6 rule, not a hypothesis test"
        )
    else:
        if n != RULE_SEEDS:
            raise Refusal(
                f"N = {n}: the M-6 rule needs {RULE_SEEDS} seeds "
                "(--exploratory for another N)"
            )
        if sorted(seeds) != sorted(HELD_OUT):
            raise Refusal(
                f"seeds {seeds}: the M-6 rule compares the held-out "
                f"{HELD_OUT[0]} to {HELD_OUT[-1]} only (--exploratory)"
            )
        if dirty:
            raise Refusal("a record was made with uncommitted analysis code")
        minimum = RULE_MINIMUM
        label = LABEL
    return {
        "label": label,
        "mode": "exploratory" if exploratory else "rule",
        "n_seeds": n,
        "minimum": minimum,
        "seeds": seeds,
        "n_repeated_seeds": repeated,
        "analysis_commit": commits.pop(),
        "analysis_dirty": dirty,
        "preset": presets.pop(),
        "run_commits": [r["contrib"]["run"].get("commit") for r in records],
        "dirs": [str(r["dir"]) for r in records],
    }


def load(directory: Path) -> dict:
    """One seed's two records; refuse a forbidden word in either text."""
    out = {"dir": directory}
    for key, name in (("contrib", "contrib.json"), ("ce", "ce.json")):
        text = (directory / name).read_text()
        hit = FORBIDDEN.search(text)
        if hit:
            raise Refusal(f"{directory / name} contains {hit.group(0)!r}")
        out[key] = json.loads(text)
    return out


# --------------------------------------------------------------- assemble
def replicate(records: list[dict], exploratory: bool) -> dict:
    """The replication record: metadata, every row classified, a summary."""
    meta = check_records(records, exploratory)
    per_seed = [seed_rows(r["contrib"], r["ce"]) for r in records]
    keys = sorted(set().union(*per_seed))
    rows = []
    for key in keys:
        readings = [s.get(key) for s in per_seed]
        rows.append(
            {
                **dict(zip(ROW_FIELDS, key)),
                "readings": [r.word if r else None for r in readings],
                "claims": [
                    [c.text() for c in r.claims] if r else None
                    for r in readings
                ],
                **classify(readings, meta["minimum"]),
            }
        )
    summary: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        summary[row["family"]][row["class"]] += 1
        summary[row["family"]]["rows"] += 1
        if row["replicated_claims"]:
            summary[row["family"]]["with replicated claim"] += 1
        if row["n_absent"]:
            summary[row["family"]]["absent on some seed"] += 1
    return {
        **meta,
        "rule": (
            "replicated: one claim-bearing reading on at least "
            f"{meta['minimum']} of {meta['n_seeds']} seeds and no pair of "
            "seeds with jointly unsatisfiable claims; contradicted: some "
            "such pair; else not replicated. Fallback: atomic claims implied "
            f"on at least {meta['minimum']} seeds and contradicted by none."
        ),
        "constants": {
            "ratio_margin": RATIO_MARGIN,
            "retain_level": RETAIN_LEVEL,
            "near_zero": NEAR_ZERO,
            "heavy_tail": HEAVY_TAIL,
            "light_tail": LIGHT_TAIL,
            "unimodal_bc": UNIMODAL_BC,
        },
        "vocabulary": VOCABULARY,
        "tool": base.git_state(),
        "summary": {f: dict(c) for f, c in sorted(summary.items())},
        "rows": rows,
    }


# ---------------------------------------------------------------- markdown
CLASSES = ("replicated", "contradicted", "not replicated")


def markdown(record: dict) -> str:
    label = record["label"]
    seeds = record["seeds"]
    lines = [
        "# Phase J replication (rule M-6)",
        "",
        f"**{label}.** Seeds {', '.join(seeds)}; analysis commit "
        f"`{record['analysis_commit']}` (dirty: {record['analysis_dirty']}); "
        f"preset {record['preset']}; mode {record['mode']}, at least "
        f"{record['minimum']} of {record['n_seeds']}"
        + (
            f"; {record['n_repeated_seeds']} repeated seed(s)"
            if record["n_repeated_seeds"]
            else ""
        )
        + ". No pooling across seeds. Readings and claims are estimates on "
        "development seeds; no pass or fail.",
        "",
        f"Rule: {record['rule']}",
        "",
        "## Summary by family",
        "",
        "| family | rows | replicated | contradicted | not replicated | "
        "with replicated claim | absent on some seed |",
        "|---|---|---|---|---|---|---|",
    ]
    for family, c in record["summary"].items():
        lines.append(
            f"| {family} | {c.get('rows', 0)} | "
            + " | ".join(
                str(c.get(k, 0))
                for k in (*CLASSES, "with replicated claim",
                          "absent on some seed")
            )
            + " |"
        )
    lines += [
        "",
        "## Claims of every reading word",
        "",
        "A word with claims `none` never contradicts and never counts toward "
        "the minimum.",
        "",
        "| row type | word | claims |",
        "|---|---|---|",
    ]
    for kind, words in record["vocabulary"].items():
        for word, claims in words.items():
            lines.append(f"| {kind} | {word} | {claims} |")
    by_family: dict[str, list] = defaultdict(list)
    for row in record["rows"]:
        by_family[row["family"]].append(row)
    head = (
        "| system | decision | profile | horizon | item | "
        + " | ".join(seeds)
        + " | class | replicated reading or claims |"
    )
    rule = "|---|---|---|---|---|" + "---|" * len(seeds) + "---|---|"
    for family, rows in sorted(by_family.items()):
        lines += [
            "",
            f"## {family}",
            "",
            head,
            rule,
        ]
        for row in rows:
            what = row["replicated_reading"] or "; ".join(
                row["replicated_claims"]
            )
            if row["class"] == "contradicted":
                first = row["contradicting_pairs"][0]
                what = (
                    f"{seeds[first[0]]} {first[1]} vs {seeds[first[2]]} "
                    f"{first[3]}" + (f"; claims: {what}" if what else "")
                )
            lines.append(
                f"| {row['system']} | {row['decision']} | {row['profile']} | "
                f"{row['horizon']} | {row['item']} | "
                + " | ".join(w if w is not None else "(absent)"
                             for w in row["readings"])
                + f" | {row['class']} | {what} |"
            )
    return base.label_tables("\n".join(lines) + "\n", label)


# -------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any(FORBIDDEN.search(a) for a in argv):
        print("lpc_replicate: refused: confirmatory", file=sys.stderr)
        return 64
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("dirs", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--exploratory", action="store_true")
    args = parser.parse_args(argv)
    try:
        records = [load(d) for d in args.dirs]
        record = replicate(records, args.exploratory)
    except (Refusal, KeyError, ValueError, FileNotFoundError) as err:
        print(f"lpc_replicate: refused: {err!r}", file=sys.stderr)
        return 64
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "replication.json").write_text(
        json.dumps(base.to_json(record), indent=1, allow_nan=False) + "\n"
    )
    (args.out / "replication.md").write_text(markdown(record))
    print(f"wrote {args.out}/replication.json and replication.md",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
