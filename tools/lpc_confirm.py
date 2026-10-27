#!/usr/bin/env python3
"""Phase J confirmatory verdicts on the pre-registered claim table (WU-0054).

The tool reads the claim table ``claims.json`` of the pre-registration
(``docs/study/preregistration_phase_j/``, WU-0053) and, for each of N seeds,
the A/B/D record ``contrib.json`` and the C/E record ``ce.json`` of one
analysis commit. It builds every seed's reading rows exactly as
``tools/lpc_replicate.py`` does (``seed_rows``), keeps only the rows the
claim table names, and applies the table's rule (``claims["rule"]``, DC-2,
DC-5):

* **per row:** *confirmed* if the row's claim is implied by the reading on at
  least ``claims["minimum"]`` (4) seeds among those present and no two present
  seeds have jointly unsatisfiable interval claims; *contradicted* if some
  such pair exists; *not confirmable* if fewer than ``minimum`` seeds are
  present; otherwise *not confirmed*. Implication and contradiction are
  ``lpc_replicate.implies`` and ``lpc_replicate.contradict``, so point claims
  never establish a contradiction (S3);
* **per claim and system:** *confirmed* if every row of that system is
  confirmed; *contradicted* if any is contradicted; *not confirmable* if any
  is not confirmable and none is contradicted; otherwise *not confirmed*.

A seed is *absent* for a system when its run's validation gate for that
system failed (``results.json``: ``systems/<s>/validation/gate/gate_pass``),
unless ``--ignore-gate`` (rehearsal only) is given. Nothing is reported for a
row outside the claim table.

Source rows (J-I1, J-C2; ledger seq 53) are not ``lpc_replicate`` rows: they
name a ``source`` (the run's ``results.json`` or the seed's ``ce.json``) and
a ``path`` in it, and ``claims["reading_tables"][<claim id>]`` maps each
word to its threshold claims. J-I1 reads the stored Q-N word; J-C2 derives
its word from the stored interval (above target if ``ci[0] > 0.10``, below
target if ``ci[1] < 0.10``, else not determined). Their claims enter the
same rule.

Secondary description (pre-registration section 7a): ``v3.json`` and
``v3.md`` list, for each v3 row and system, the word on each seed from the
run's ``results.json`` ``verdicts`` block ("gate failed" for a system whose
gate failed) and the count of seeds per word, labeled :data:`V3_LABEL` (the
rehearsal label with ``--rehearsal``). No combined word; CONF-1's words are
not read.

Usage::

    python tools/lpc_confirm.py \
        --claims docs/study/preregistration_phase_j/claims.json \
        --pinned docs/study/preregistration_phase_j/lyapunov.json \
        <seed dir> ... --out <dir> [--rehearsal] [--ignore-gate]

Each ``<seed dir>`` holds one seed's ``contrib.json`` and ``ce.json`` and
lies beside the run folder those records name: the run is
``<seed dir>/../<name>``, where ``<name>`` is the last component of the
records' ``run.dir``, and the component before it must equal the name of the
seed dir's parent (the layout ``<root>/<run>/contrib-*/`` beside
``<root>/<run>/<preset>/``). The run's ``results.json`` gives the gates and
``cache/lyapunov.json`` the Lyapunov cache. Writes ``confirm.json``,
``confirm.md``, ``v3.json`` and ``v3.md``.

Modes
    Without ``--rehearsal`` (sealed mode) every run must be sealed
    (``provenance.seed_kind`` "confirmatory", seed id ``CONF-n``), the seed
    ids must be exactly the table's ``seed_ids``, every record must carry the
    sealed label of ``tools/lpc_contrib.py --sealed`` and be made with
    committed analysis code, ``--pinned`` must hash to the pinned sha256 of
    ``tools/lpc_contrib.py`` and every run's ``cache/lyapunov.json`` must
    equal it byte for byte (by sha256), and ``--ignore-gate`` is refused.
    The output is labeled "PHASE J CONFIRMATORY (...): pre-registered
    verdicts, UNPROMOTED".

    With ``--rehearsal`` every run must be a development run (``DEV-n``)
    whose records carry the DEVELOPMENT label; the cache hashes are reported,
    not enforced; any N >= 1 of distinct seeds runs, the minimum stays the
    table's; and everything is labeled "DEVELOPMENT REHEARSAL: not a
    hypothesis test".

Refusals (exit 64, nothing written): a malformed claim table (schema, a
claim that is not ``quantity op value``, a quantity that the row's family
cannot carry, a row named twice in one claim); a seed id repeated; analysis
commits that differ (contrib and ce, every seed) or presets that differ; a
C/E record of another run or without its A/D record; a run whose
``results.json`` names another seed or run commit, is incomplete, or lacks a
gate flag; a pre-registered row missing from a present seed's records, or
matched twice; an unknown reading word or an uncovered reading leaf, and a
C1 row that differs from its D source (both from ``lpc_replicate``); and the
mode refusals above.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import lpc_contrib as base  # noqa: E402
import lpc_replicate as rep  # noqa: E402
from lpcstudy import contribution as cb  # noqa: E402

Refusal = base.Refusal
SCHEMA = "lpcstudy.phase-j-claims/1"
ROW_KEYS = ("family", "system", "profile", "horizon", "item")
FAMILY_QUANTITY = {
    "A drop-one": "ratio",
    "A vs separation": "ratio",
    "B loss ratio": "ratio",
    "D vs full": "ratio",
    "D vs below": "ratio",
    "C1": "ratio",
    "C2 ratio": "ratio",
    "C3 ratio": "ratio",
    "B pair": "delta",
    "C2 retained": "retained",
}
"""The quantity a family's reading words make claims on (``lpc_replicate``
vocabulary). A claim on another quantity could never be implied, so the
table is refused rather than read as "not confirmed"."""
CLAIM_PATTERN = re.compile(r"(\S+) (<=|>=|<|>) (\S+)")
CONFIRMED = "confirmed"
CONTRADICTED = "contradicted"
NOT_CONFIRMABLE = "not confirmable"
NOT_CONFIRMED = "not confirmed"
VERDICTS = (CONFIRMED, CONTRADICTED, NOT_CONFIRMABLE, NOT_CONFIRMED)
REHEARSAL_LABEL = "DEVELOPMENT REHEARSAL: not a hypothesis test"
SEALED_LABEL = (
    "PHASE J CONFIRMATORY ({seeds}): pre-registered verdicts, UNPROMOTED"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------- claim table
def parse_text(text: str) -> rep.Claim:
    """``quantity op value`` as an interval claim."""
    match = CLAIM_PATTERN.fullmatch(str(text))
    if match is None:
        raise Refusal(f"claim {text!r} is not 'quantity op value'")
    quantity, op, value = match.groups()
    try:
        number = float(value)
    except ValueError:
        raise Refusal(f"claim {text!r}: {value!r} is not a number") from None
    return rep.Claim(quantity, op, number)


def parse_claim(text: str, family: str) -> rep.Claim:
    """The claim of an ``lpc_replicate`` row, on its family's quantity."""
    claim = parse_text(text)
    expected = FAMILY_QUANTITY.get(family)
    if expected is None:
        raise Refusal(f"family {family!r} is not supported by the rule")
    if claim.quantity != expected:
        raise Refusal(
            f"claim {text!r}: rows of {family!r} make claims on "
            f"{expected!r}, not {claim.quantity!r}"
        )
    return claim


# ------------------------------------------------- rows read from a source
# J-I1 and J-C2 (ledger seq 53) are not rows of ``lpc_replicate``: each names
# a ``source`` document and a ``path`` in it, and claims.json's
# ``reading_tables[<claim id>]`` gives the claims of each word. The words are
# threshold claims on one quantity, so implication and contradiction are
# ``lpc_replicate.implies`` and ``contradict`` (bounds on a real line).
SOURCES = {"pipeline results.json": "results", "ce.json": "ce"}
"""A source row's document: the run's ``results.json`` or the seed's
``ce.json``."""
SOURCE_ROW_KEYS = ("source", "system", "profile", "path", "item")


def word_claims(table: dict, claim_id: str) -> dict[str, tuple]:
    """The claims of every word of a claim's reading table."""
    words = table.get("reading_tables", {}).get(claim_id, {}).get("words")
    if not words:
        raise Refusal(f"{claim_id}: no reading table")
    return {w: tuple(parse_text(c) for c in cs) for w, cs in words.items()}


def read_stored_word(node: dict, words: dict) -> str:
    """J-I1: the frozen Q-N reading stored with the interval."""
    return node.get("reading")


def read_ci_threshold(node: dict, words: dict) -> str:
    """J-C2: "above target" if ci[0] > t, "below target" if ci[1] < t,
    otherwise "not determined"; t from the two words' claims."""
    (above,), (below,) = words["above target"], words["below target"]
    if (above.op, below.op) != (">", "<") or above.value != below.value:
        raise Refusal("J-C2: the target words do not share one threshold")
    lower, upper = node["ci"]
    if lower is not None and lower > above.value:
        return "above target"
    if upper is not None and upper < above.value:
        return "below target"
    return "not determined"


SOURCE_READERS = {"J-I1": read_stored_word, "J-C2": read_ci_threshold}
"""The reader of each source claim's reading table (claims.json, seq 53)."""


def row_claim(table: dict, claim: dict, row: dict) -> rep.Claim:
    """The parsed claim of one row of the table, checked against its kind."""
    if "source" not in row:
        return parse_claim(claim["claim"], row["family"])
    if row["source"] not in SOURCES:
        raise Refusal(f"{claim['id']}: unknown source {row['source']!r}")
    if claim["id"] not in SOURCE_READERS:
        raise Refusal(f"{claim['id']}: no reader for its reading table")
    target = parse_text(claim["claim"])
    quantities = {
        c.quantity
        for cs in word_claims(table, claim["id"]).values()
        for c in cs
    }
    if quantities != {target.quantity}:
        raise Refusal(
            f"{claim['id']}: reading-table quantities {sorted(quantities)}, "
            f"claim on {target.quantity!r}"
        )
    return target


def row_key(row: dict) -> tuple:
    keys = SOURCE_ROW_KEYS if "source" in row else ROW_KEYS
    return tuple(row[k] for k in keys)


def source_reading(table: dict, claim_id: str, spec: dict, seed: dict):
    """One seed's reading of a source row (refuse a missing path)."""
    node = seed[SOURCES[spec["source"]]]
    for part in spec["path"].split("/"):
        if not isinstance(node, dict) or part not in node:
            raise Refusal(
                f"{seed['dir']}: pre-registered row {spec['path']!r} is "
                f"missing from {spec['source']}"
            )
        node = node[part]
    words = word_claims(table, claim_id)
    word = SOURCE_READERS[claim_id](node, words)
    if word not in words:
        raise Refusal(f"{claim_id}: unknown reading {word!r} at {spec['path']}")
    return rep.Reading(word, words[word], f"{spec['source']}:{spec['path']}")


def load_claims(path: Path) -> dict:
    """The claim table, checked; each row gains its parsed claim."""
    table = json.loads(path.read_text())
    if table.get("schema") != SCHEMA:
        raise Refusal(f"{path}: schema {table.get('schema')!r}, not {SCHEMA}")
    minimum = table.get("minimum")
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
        raise Refusal(f"{path}: minimum {minimum!r} is not a positive integer")
    if not table.get("claims"):
        raise Refusal(f"{path}: no claims")
    ids = [c["id"] for c in table["claims"]]
    if len(set(ids)) != len(ids):
        raise Refusal(f"{path}: a claim id is repeated")
    for claim in table["claims"]:
        seen = set()
        for row in claim["rows"]:
            key = row_key(row)
            if key in seen:
                raise Refusal(f"{claim['id']}: row {key} is named twice")
            seen.add(key)
            row_claim(table, claim, row)
    return table


# ------------------------------------------------------------------- seeds
def run_folder(seed_dir: Path, recorded: str) -> Path:
    """The run folder beside ``seed_dir`` that the records name."""
    named = Path(recorded)
    parent = seed_dir.resolve().parent
    if len(named.parts) < 2 or named.parts[-2] != parent.name:
        raise Refusal(
            f"{seed_dir}: the records name run {recorded!r}, which is not "
            f"beside this folder (expected .../{parent.name}/<run>)"
        )
    return parent / named.name


def load_seed(directory: Path) -> dict:
    """One seed's two records, its run's ``results.json`` and cache hash."""
    contrib_path, ce_path = directory / "contrib.json", directory / "ce.json"
    contrib = json.loads(contrib_path.read_text())
    ce = json.loads(ce_path.read_text())
    run = run_folder(directory, str(contrib["run"]["dir"]))
    results_path = run / "results.json"
    cache_path = run / "cache" / "lyapunov.json"
    if not cache_path.exists():
        raise Refusal(f"{run}: no cache/lyapunov.json")
    return {
        "dir": directory,
        "run": run,
        "contrib": contrib,
        "ce": ce,
        "results": json.loads(results_path.read_text()),
        "sha256": {
            "contrib.json": sha256(contrib_path),
            "ce.json": sha256(ce_path),
            "results.json": sha256(results_path),
            "lyapunov.json": sha256(cache_path),
        },
    }


def gate_flags(results: dict, where: str) -> dict[str, bool]:
    """``gate_pass`` of every system of the run; refuse a missing flag."""
    flags = {}
    for system, res in results["systems"].items():
        flag = res.get("validation", {}).get("gate", {}).get("gate_pass")
        if not isinstance(flag, bool):
            raise Refusal(f"{where}: no gate_pass flag for {system}")
        flags[system] = flag
    return flags


def check_seeds(
    seeds: list[dict],
    table: dict,
    pinned_sha: str,
    rehearsal: bool,
    ignore_gate: bool,
) -> dict:
    """Every refusal on the seeds; the metadata of the evaluation."""
    if not seeds:
        raise Refusal("no seed folders")
    if ignore_gate and not rehearsal:
        raise Refusal("--ignore-gate is a rehearsal option only")
    if not rehearsal and pinned_sha != base.PINNED_LYAPUNOV_SHA256:
        raise Refusal(
            f"--pinned has sha256 {pinned_sha}, not the pinned "
            f"{base.PINNED_LYAPUNOV_SHA256}"
        )
    ids = []
    for seed in seeds:
        contrib, ce, where = seed["contrib"], seed["ce"], str(seed["dir"])
        seed_id = str(contrib["run"]["seed_id"])
        if ce["run"]["seed_id"] != seed_id or ce["run"]["dir"] != contrib[
            "run"
        ]["dir"]:
            raise Refusal(f"{where}: ce.json of another run")
        if not ce.get("abd"):
            raise Refusal(f"{where}: ce.json without its A/D record")
        if ce["abd"]["commit"] != contrib["analysis"]["commit"]:
            raise Refusal(f"{where}: ce.json read another A/D commit")
        prov = seed["results"].get("provenance", {})
        if prov.get("seed_id") != seed_id:
            raise Refusal(
                f"{where}: results.json of {prov.get('seed_id')!r}, records "
                f"of {seed_id!r}"
            )
        if prov.get("commit") != contrib["run"].get("commit"):
            raise Refusal(f"{where}: results.json of another run commit")
        if prov.get("complete") is not True:
            raise Refusal(f"{where}: the run is not complete")
        if rehearsal:
            kind, pattern = "development", r"DEV-\d+"
            label = cb.LABEL.format(seed_id=seed_id)
        else:
            kind, pattern = "confirmatory", r"CONF-\d+"
            label = base.SEALED_LABEL.format(seed_id=seed_id)
        if prov.get("seed_kind") != kind or not re.fullmatch(pattern, seed_id):
            raise Refusal(
                f"{where}: seed_kind={prov.get('seed_kind')!r}, "
                f"seed_id={seed_id!r}: "
                + ("not a development run (--rehearsal)" if rehearsal
                   else "not a sealed run (development runs need --rehearsal)")
            )
        if contrib.get("label") != label or ce.get("label") != label:
            raise Refusal(f"{where}: records not labeled {label!r}")
        seed["gate"] = gate_flags(seed["results"], where)
        seed["lyapunov_matches_pinned"] = (
            seed["sha256"]["lyapunov.json"] == pinned_sha
        )
        if not rehearsal and not seed["lyapunov_matches_pinned"]:
            raise Refusal(
                f"{seed['run']}/cache/lyapunov.json has sha256 "
                f"{seed['sha256']['lyapunov.json']}, not the pinned "
                f"{pinned_sha}"
            )
        ids.append(seed_id)
    if len(set(ids)) != len(ids):
        raise Refusal(f"seed ids are not distinct: {ids}")
    commits = {
        s[k]["analysis"]["commit"] for s in seeds for k in ("contrib", "ce")
    }
    if len(commits) != 1:
        raise Refusal(f"different analysis commits: {sorted(commits)}")
    presets = {s["contrib"]["run"].get("preset") for s in seeds}
    if len(presets) != 1:
        raise Refusal(f"runs of different presets: {sorted(map(str, presets))}")
    dirty = any(
        s[k]["analysis"]["dirty"] for s in seeds for k in ("contrib", "ce")
    )
    if not rehearsal:
        if sorted(ids) != sorted(table["seed_ids"]):
            raise Refusal(
                f"seeds {ids}: the pre-registered seeds are "
                f"{table['seed_ids']}"
            )
        if dirty:
            raise Refusal("a record was made with uncommitted analysis code")
    label = (
        REHEARSAL_LABEL
        if rehearsal
        else SEALED_LABEL.format(seeds=", ".join(ids))
    )
    return {
        "label": label,
        "mode": "rehearsal" if rehearsal else "sealed",
        "ignore_gate": ignore_gate,
        "seeds": ids,
        "minimum": table["minimum"],
        "analysis_commit": commits.pop(),
        "analysis_dirty": dirty,
        "preset": presets.pop(),
    }


# ---------------------------------------------------------------- the rule
def row_verdict(readings: list, claim: rep.Claim, minimum: int) -> dict:
    """The verdict of one row from its seeds' readings (``None``: absent)."""
    present = [(i, r) for i, r in enumerate(readings) if r is not None]
    implying = [
        r is not None and rep.implies(r.claims, claim) for r in readings
    ]
    pairs = [
        [i, a.word, j, b.word]
        for n, (i, a) in enumerate(present)
        for j, b in present[n + 1 :]
        if rep.contradict(a.claims, b.claims)
    ]
    n_implying = sum(implying)
    if n_implying >= minimum and not pairs:
        verdict = CONFIRMED
    elif pairs:
        verdict = CONTRADICTED
    elif len(present) < minimum:
        verdict = NOT_CONFIRMABLE
    else:
        verdict = NOT_CONFIRMED
    return {
        "verdict": verdict,
        "n_present": len(present),
        "n_implying": n_implying,
        "implying": implying,
        "contradicting_pairs": pairs,
    }


def system_verdict(verdicts: list[str]) -> str:
    """The verdict of one claim on one system from its rows' verdicts."""
    if all(v == CONFIRMED for v in verdicts):
        return CONFIRMED
    if CONTRADICTED in verdicts:
        return CONTRADICTED
    if NOT_CONFIRMABLE in verdicts:
        return NOT_CONFIRMABLE
    return NOT_CONFIRMED


def find_row(rows: dict, spec: dict, where: str):
    """The one reading row of a seed that a pre-registered row names."""
    want = tuple(spec[k] for k in ROW_KEYS)
    found = [
        key
        for key in rows
        if (key[1], key[0], key[3], key[4], key[5]) == want
    ]
    if not found:
        raise Refusal(f"{where}: pre-registered row {want} is missing")
    if len(found) > 1:
        raise Refusal(f"{where}: pre-registered row {want} matches {found}")
    return rows[found[0]]


def evaluate(table: dict, seeds: list[dict], meta: dict) -> dict:
    """Rows and claim-by-system verdicts of the pre-registered table."""
    per_seed = [rep.seed_rows(s["contrib"], s["ce"]) for s in seeds]
    minimum = table["minimum"]
    rows, verdicts = [], []
    for claim in table["claims"]:
        by_system: dict[str, list[str]] = {}
        for spec in claim["rows"]:
            parsed = row_claim(table, claim, spec)
            system = spec["system"]
            absent, readings = [], []
            for seed, seed_rows in zip(seeds, per_seed):
                if system not in seed["gate"]:
                    raise Refusal(f"{seed['dir']}: no system {system!r}")
                gone = not seed["gate"][system] and not meta["ignore_gate"]
                absent.append(gone)
                if gone:
                    readings.append(None)
                elif "source" in spec:
                    readings.append(
                        source_reading(table, claim["id"], spec, seed)
                    )
                else:
                    readings.append(
                        find_row(seed_rows, spec, str(seed["dir"]))
                    )
            out = row_verdict(readings, parsed, minimum)
            identity = {
                "family": spec.get("family", spec.get("source")),
                "system": system,
                "profile": spec["profile"],
                "horizon": spec.get("horizon", ""),
                "item": spec["item"],
            }
            if "source" in spec:
                identity |= {"source": spec["source"], "path": spec["path"]}
            rows.append(
                {
                    "claim_id": claim["id"],
                    **identity,
                    "claim": claim["claim"],
                    "readings": [r.word if r else None for r in readings],
                    "reading_claims": [
                        [c.text() for c in r.claims] if r else None
                        for r in readings
                    ],
                    "absent": absent,
                    **out,
                }
            )
            by_system.setdefault(system, []).append(out["verdict"])
        for system, row_verdicts in by_system.items():
            verdicts.append(
                {
                    "claim_id": claim["id"],
                    "system": system,
                    "verdict": system_verdict(row_verdicts),
                    "rows": len(row_verdicts),
                    "row_verdicts": dict(Counter(row_verdicts)),
                }
            )
    return {"rows": rows, "verdicts": verdicts}


def confirm(
    table: dict,
    claims_path: Path,
    pinned_path: Path,
    seeds: list[dict],
    rehearsal: bool,
    ignore_gate: bool,
) -> dict:
    """The confirm record: metadata, inputs, rows and verdicts."""
    pinned_sha = sha256(pinned_path)
    meta = check_seeds(seeds, table, pinned_sha, rehearsal, ignore_gate)
    meta["c1_rows_checked"] = [
        rep.check_c1(s["contrib"], s["ce"], str(s["dir"])) for s in seeds
    ]
    result = evaluate(table, seeds, meta)
    summary = Counter(r["verdict"] for r in result["rows"])
    return {
        **meta,
        "rule": table["rule"],
        "claims": {"path": str(claims_path), "sha256": sha256(claims_path)},
        "pinned_lyapunov": {"path": str(pinned_path), "sha256": pinned_sha},
        "inputs": [
            {
                "seed_id": s["contrib"]["run"]["seed_id"],
                "dir": str(s["dir"]),
                "run": str(s["run"]),
                "sha256": s["sha256"],
                "lyapunov_matches_pinned": s["lyapunov_matches_pinned"],
                "gate_pass": s["gate"],
            }
            for s in seeds
        ],
        "tool": base.git_state(),
        "row_summary": {v: summary.get(v, 0) for v in VERDICTS},
        **result,
    }


# ------------------------------------------- secondary v3 description (7a)
V3_LABEL = (
    "SECONDARY DESCRIPTION: v3 words of the sealed runs under the phase J "
    "configuration; not the v3 test; does not change, confirm or replace "
    "CONF-1"
)
GATE_FAILED = "gate failed"
MISSING = "(missing)"
V3_DEPARTURES = (
    "n_test is 4000, not v3's 1000, so the intervals are narrower than v3 "
    "sized them",
    "the device is the GPU, where v3 section 9 makes the CPU official",
    "the robustness sweep is skipped (it is reported-only in v3)",
    "the time unit is pinned (pre-registration section 5)",
)
"""Pre-registration section 7a: stated with the table."""


def v3_description(seeds: list[dict], rehearsal: bool) -> dict:
    """The v3 word of every row and system on every seed (section 7a).

    Read from each run's ``results.json`` ``verdicts`` block
    (``verdicts[<row>]["by_system"][<system>]``). A system whose gate failed
    on a seed reads "gate failed" there; a row or system a seed lacks reads
    "(missing)" and is counted. No combined word, no seed-level verdict, no
    pooling, and no CONF-1 word (added to the report by hand).
    """
    ids = [str(s["contrib"]["run"]["seed_id"]) for s in seeds]
    blocks = [s["results"].get("verdicts") or {} for s in seeds]
    names = list(dict.fromkeys(k for b in blocks for k in b))
    rows, missing = [], 0
    for name in names:
        systems = list(
            dict.fromkeys(
                sys_name
                for b in blocks
                for sys_name in (b.get(name) or {}).get("by_system", {})
            )
        )
        for system in systems:
            words = []
            for seed, block in zip(seeds, blocks):
                by_system = (block.get(name) or {}).get("by_system", {})
                if seed["gate"].get(system) is False:
                    words.append(GATE_FAILED)
                elif system in by_system:
                    words.append(str(by_system[system]))
                else:
                    words.append(MISSING)
                    missing += 1
            rows.append(
                {
                    "row": name,
                    "system": system,
                    "words": words,
                    "count": dict(Counter(words)),
                }
            )
    return {
        "label": REHEARSAL_LABEL if rehearsal else V3_LABEL,
        "seeds": ids,
        "departures": list(V3_DEPARTURES),
        "n_missing": missing,
        "rows": rows,
    }


def v3_markdown(record: dict) -> str:
    label, seeds = record["label"], record["seeds"]
    lines = [
        "# Secondary description: v3 words of the phase J runs",
        "",
        f"**{label}.** Seeds {', '.join(seeds)}. For each v3 row and system, "
        "the word on each seed (``results.json`` verdicts) and the count of "
        "seeds per word. No combined word, no confirmed or not confirmed, "
        "no pooled statistic. A system that failed the validation gate on a "
        f"seed reads \"{GATE_FAILED}\". Cells read \"{MISSING}\": "
        f"{record['n_missing']}. CONF-1's words are not read here.",
        "",
        "Departures from v3: "
        + "; ".join(f"({i}) {d}" for i, d in
                    enumerate(record["departures"], 1))
        + ".",
        "",
        "| row | system | " + " | ".join(seeds) + " | seeds per word |",
        "|---|---|" + "---|" * len(seeds) + "---|",
    ]
    for r in record["rows"]:
        counts = ", ".join(f"{w} {n}" for w, n in r["count"].items())
        lines.append(
            f"| {r['row']} | {r['system']} | " + " | ".join(r["words"])
            + f" | {counts} |"
        )
    return base.label_tables("\n".join(lines) + "\n", label)


# ---------------------------------------------------------------- markdown
def markdown(record: dict) -> str:
    label, seeds = record["label"], record["seeds"]
    lines = [
        "# Phase J confirmatory verdicts",
        "",
        f"**{label}.** Seeds {', '.join(seeds)}; mode {record['mode']}"
        + ("; validation gates ignored (--ignore-gate)"
           if record["ignore_gate"] else "")
        + f"; analysis commit `{record['analysis_commit']}` (dirty: "
        f"{record['analysis_dirty']}); preset {record['preset']}; claim "
        f"table `{record['claims']['path']}` (sha256 "
        f"`{record['claims']['sha256']}`); pinned Lyapunov cache sha256 "
        f"`{record['pinned_lyapunov']['sha256']}`. At least "
        f"{record['minimum']} seeds; no pooling across seeds.",
        "",
        f"Rule: {record['rule']}",
        "",
        "## Inputs",
        "",
        "| seed | gate pass | cache equals pinned | cache sha256 |",
        "|---|---|---|---|",
    ]
    for item in record["inputs"]:
        gates = ", ".join(f"{s} {v}" for s, v in item["gate_pass"].items())
        lines.append(
            f"| {item['seed_id']} | {gates} | "
            f"{item['lyapunov_matches_pinned']} | "
            f"`{item['sha256']['lyapunov.json']}` |"
        )
    lines += [
        "",
        "## Verdicts by claim and system",
        "",
        "| claim | system | verdict | rows | row verdicts |",
        "|---|---|---|---|---|",
    ]
    for v in record["verdicts"]:
        counts = ", ".join(f"{k} {n}" for k, n in v["row_verdicts"].items())
        lines.append(
            f"| {v['claim_id']} | {v['system']} | **{v['verdict']}** | "
            f"{v['rows']} | {counts} |"
        )
    head = (
        "| system | profile | horizon | item | "
        + " | ".join(seeds)
        + " | implying | verdict |"
    )
    rule = "|---|---|---|---|" + "---|" * len(seeds) + "---|---|"
    for claim_id in dict.fromkeys(r["claim_id"] for r in record["rows"]):
        rows = [r for r in record["rows"] if r["claim_id"] == claim_id]
        lines += [
            "",
            f"## {claim_id}: {rows[0]['family']}, claim `{rows[0]['claim']}`",
            "",
            head,
            rule,
        ]
        for r in rows:
            cells = [
                "(absent: gate)" if gone else str(word)
                for word, gone in zip(r["readings"], r["absent"])
            ]
            lines.append(
                f"| {r['system']} | {r['profile']} | {r['horizon']} | "
                f"{r['item']} | " + " | ".join(cells)
                + f" | {r['n_implying']} of {r['n_present']} | "
                f"{r['verdict']} |"
            )
    return base.label_tables("\n".join(lines) + "\n", label)


# -------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("dirs", type=Path, nargs="+")
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--pinned", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rehearsal", action="store_true")
    parser.add_argument("--ignore-gate", action="store_true")
    args = parser.parse_args(argv)
    try:
        table = load_claims(args.claims)
        seeds = [load_seed(d) for d in args.dirs]
        record = confirm(
            table,
            args.claims,
            args.pinned,
            seeds,
            args.rehearsal,
            args.ignore_gate,
        )
        v3 = v3_description(seeds, args.rehearsal)
    except (Refusal, KeyError, ValueError, FileNotFoundError) as err:
        print(f"lpc_confirm: refused: {err!r}", file=sys.stderr)
        return 64
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "confirm.json").write_text(
        json.dumps(base.to_json(record), indent=1, allow_nan=False) + "\n"
    )
    (args.out / "confirm.md").write_text(markdown(record))
    (args.out / "v3.json").write_text(
        json.dumps(base.to_json(v3), indent=1, allow_nan=False) + "\n"
    )
    (args.out / "v3.md").write_text(v3_markdown(v3))
    if v3["n_missing"]:
        print(f"warning: {v3['n_missing']} v3 cell(s) missing", file=sys.stderr)
    print(
        f"wrote {args.out}/confirm.json and confirm.md: "
        + ", ".join(f"{k} {n}" for k, n in record["row_summary"].items())
        + " (rows)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
