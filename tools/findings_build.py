#!/usr/bin/env python3
"""Build and check the preliminary findings document (WU-0020).

The study asks whether four local predictability conditions decide how to
blend an analog forecaster (CP) with a physics-based forecaster (PLP). When
the sealed confirmatory run finishes, the owner and the student need one
short, honest document that says what came out. This tool writes that
document from the stored results and then proves that it says nothing else.

Two commands:

* ``render`` reads the official ``results.json`` (with the ``RESULTS.md`` next
  to it), the cross-check ``results.json`` and the ``compare_runs`` text. It
  fills the template ``tools/findings/preliminary.template.md`` and writes
  the document, a trace file (one row per quoted value, with its source and
  leaf path), a ``sources.json`` (paths, SHA-256 hashes, manifest hashes and
  the release reference) and three figures (F1 primary forest plot, F2
  secondary forest plot, F3 cross-check).
* ``check`` re-reads the sources, verifies their hashes, and renders the
  document again from scratch. The new text must equal the document byte for
  byte, except in two free slots: the body of section 11 (the student's
  words) and dated lines appended to section 9 (``- YYYY-MM-DD: text``, a
  real date not before the run ended). Rendering is deterministic, so any
  other edit, including an edited sentence or a swapped figure, fails.
  The rules for the free slots (threat model: accidental misstatement by a
  student, not a hostile author; the owner reads every claim in them, and
  so does the WU-0020.8 reviewer). Every line is normalized once before the checks:
  NFKC, and ``*``, ``_`` and the backtick are cut before words, stems and
  brackets are matched, so ``__CONFIRMATORY__``, ``PRO*MOTED*`` and
  ``un_promoted`` are found; leading ``>`` and list marks are cut before the
  heading tests. A line is refused if it has an invisible format character
  (Unicode category Cf), an HTML entity ``&...;``, an HTML tag or comment, or
  a letter outside the Latin script (Rössler passes; a Cyrillic look-alike
  does not). There is no numeric character of any kind (write numbers as
  words; only the 14 hypothesis names such as H2a are allowed). There is no
  heading (a ``#`` line, or a line underlined by a line of only ``=`` or
  ``-``, also inside a quote or a list item), no bracketed capitalized token
  ``[...]`` with any inner text (fullwidth brackets included), and no dated
  line later than the day ``check`` runs (``date.today()``) or earlier than
  the end of the official run. There is none of the words in
  ``banned_phrases`` and ``free_slot_refused`` (whole words,
  case-insensitive: promoted, pre-registered, provisional, verified, gate and
  others) and no word that begins with one of the stems in
  ``free_slot_stems`` of ``design_constants.json``: prove, provin, confirm,
  signific, demonstrat, breakthrough, gate, gating, provision, promot,
  unpromot, verif, unverif, pre-regist, preregist, developm, preliminar (so
  proved, confirmed, significantly, gates, provisionally and promotion are
  refused). Number words ("forty-two"), words split by a hyphen or a space
  ("pro-moted"), mid-word forms ("unconfirmed", "disproved") and claims
  phrased in other words cannot be detected, and a real date is a small
  number channel. False positives a student will hit, each refused with a
  message that names the rule: "provenance", "province", "proverb", "proven",
  "gateway", "gated", "development", "verify", "verification", "confirm",
  "demonstrates", "preliminary", "promote", "significant"; a Markdown link
  with a capitalized label such as ``[Lorenz attractor](...)``; a checked task
  box ``[X]``; a line followed by a line of a single ``-``; a letter that is
  not Latin (Greek mu). Reword, or ask the owner.

The tool only reads and formats. It computes no statistic and no verdict: a
verdict word in the document is the string stored in the results file, and no
interval is compared with a band. Figures draw the stored estimates and
interval endpoints as they are. Constants of the v3 design (bands, levels,
bars) come from ``tools/findings/design_constants.json``, each with its v3
section. Nothing in ``lpcstudy/`` is imported or changed.

Release guard (an owner checkpoint). A results file is either a development
run (``seed_kind`` development, ``seed_id`` starting ``DEV-``, no
CONFIRMATORY in the label) or a confirmatory one (``seed_kind``
confirmatory, ``seed_id`` starting ``CONF-``). Any other mix is refused. A
confirmatory build needs ``--release-ref`` of the form ``ledger-seq-<n>``, the
SHA-256 manifest hashes of the three files, and a commit equal to
``git rev-parse freeze-1^{commit}``. A ``--development`` file must be a
development run. The cross-check must be another file than the official one.
For confirmatory builds only (a development run is built whatever it
recorded), the official run must be complete, clean, a CPU run with
``LPC_THREADS`` 8, and the cross-check complete, clean and a GPU run; the
cross-check's commit may differ from the official commit and is printed with
"same as official: yes/no". The ``compare_runs`` text must name the official
run as REF and the cross-check as NEW and every differing leaf it lists must
exist in both files with the printed values; the z values themselves are not
recomputed, so an altered z in a text with the right paths is not detected.
A ``compare_runs`` text whose leaf list is empty or deleted is bound to the
two results files only by its REF and NEW paths: the owner must rerun
``compare_runs`` on the released directories and diff the result with the
committed text (a step of WU-0020.8).

Working directory (N3). In a confirmatory build ``--official``,
``--crosscheck`` and ``--td`` must be absolute paths (relative ones are
refused), they are resolved with realpath, the REF and NEW lines must be
absolute and are bound by realpath only, and ``sources.json`` stores the
resolved absolute paths, so ``check`` gives the same answer from any
directory. In a development build a REF or NEW path may be relative (it is
read against the working directory of the build, stored in ``sources.json``
as ``cwd``) and may also be bound by its last two path components; the
document then says "(development mode only)".

Cross-check commit (N2). It may differ from the official commit. In a
confirmatory build the tool then runs the read-only command ``git diff
--name-only <official>..<cross-check>`` and refuses unless every changed path
is under ``docs/agent/records/`` or is ``docs/agent/governance/ledger.jsonl``
(and refuses when git cannot answer). The command uses ``--no-renames``, so a
move out of ``lpcstudy/`` into the records lists both paths and is refused;
a path that is not valid UTF-8 or has a ``..`` component is refused. Beyond that check the tool does not
verify the commit difference: it does not look at what the changed records
say, and it needs both commits in the repository that holds the tool.

What the tool cannot verify: it does not read the ledger, so it cannot tell
that the release reference exists; and it does not read the manifest, so it
only checks that the hashes typed on the command line equal the files' hashes
(an operator who types hashes taken from the wrong file passes). The owner or
the main session must compare both with the committed manifest row and the
ledger entry.

The cross-check section also lists the stored verdict words that differ
between the two results files (``differing_words``, a string comparison of
stored leaves; nothing is recomputed). It needs the official word beside the
GPU word, so the official file is also known as the source ``official_words``,
which only a [CROSS-CHECK] section may quote; the source ``official`` stays
refused there (WU-0020.8, plan amendment of 2026-10-20).

Placeholders in the template look like ``{{official:systems/chua/H3c/ci|ci:.3g}}``:
a source name, a leaf path and an optional format. Standard library plus
matplotlib (already pinned).

Exit codes: 0 success, 1 a failed check, 2 a usage or input error.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import date
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMPLATE_PATH = HERE / "findings" / "preliminary.template.md"
CONSTANTS_PATH = HERE / "findings" / "design_constants.json"
PRELIMINARY_LINE = (
    "PRELIMINARY: internal to the owner and the student until promotion "
    "(QA.11, LPC.PC.13)."
)
MISSING = "<missing>"
NOT_RECORDED = "not recorded"
NOT_COMPUTED = "not computed"
NONE_LISTED = (
    "none listed (compare_runs prints this line only when the count is "
    "nonzero)"
)
NOT_AVAILABLE = "not available (the compare_runs text is not a TD report)"
PLACEHOLDER = re.compile(r"\{\{(\w+)(?::([^}|]*))?(?:\|([^}]*))?\}\}")
MARK = re.compile("\x00(\\d+)\x01(.*?)\x02", re.S)
# A digit may stay in untraced text only inside an identifier of the study
# (a hypothesis, a check, a decision, a work unit, a section mark). Every
# other digit is a number the trace does not explain.
IDENTIFIER = re.compile(
    r"§\s*M?\d+(?:\.\d+)?(?![\d%])"
    r"|^#{1,6} \d+\."
    r"|\bitem \d+\b(?![.\d%])"
    r"|\b(?:DEC|DEF)-\d{4}\b"
    r"|\bWU-\d{4}(?:\.\d)?\b"
    r"|\b(?:CONF|DEV)-\d\b"
    r"|\b(?:PRIME|QA|NVVUQ)\.\d+\b"
    r"|\bLPC\.PC\.\d+\b"
    r"|\bH\d[a-e]\b"
    r"|\bV[1-7]\b"
    r"|\bE[0-6]\b"
    r"|\bP[1-3]\b"
    r"|\bA[0-5]o?\b"
    r"|\bD\d{1,2}\b"
    r"|\bM[23]\b"
    r"|\bF[1-4]\b"
    r"|\bv[1-3]\b"
    r"|\br\d+\b"
    r"|\b(?:Lorenz-63|lorenz63)\b"
    r"|\bSHA-256\b"
    r"|\bfreeze-1\b"
    r"|\brho-(?:0\.5|1|2|5)%"
    r"|\bclosed_form_floor_a4o?\b"
)
DATED_LINE = re.compile(r"^- (\d{4}-\d{2}-\d{2}): ")
HYPOTHESIS_ID = re.compile(r"\bH[1-3][a-e]\b")
BRACKET_CAPITAL = re.compile(r"\[\s*[A-Z][^\]]*\]")
SETEXT_UNDERLINE = re.compile(r"(?:=+|-+)\s*")
LEADING_MARKS = re.compile(r"(?:\s*>|\s*[-*+]\s)*\s*")
MARKDOWN_NOISE = re.compile(r"[*_`]")
HTML_ENTITY = re.compile(r"&[#A-Za-z0-9]+;")
HTML_TAG = re.compile(r"<[!/?A-Za-z]")
FULL_COMMIT = re.compile(r"[0-9a-f]{40}")
RECORDS_PREFIX = "docs/agent/records/"
LEDGER_PATH = "docs/agent/governance/ledger.jsonl"
HEADING = re.compile(r"^(#{2,3}) ")
TAG = re.compile(r"\[([A-Z][A-Z-]+)(?::[^\]]*)?\]\s*$")
RELEASE_REF = re.compile(r"^ledger-seq-\d+$")
SHA_HEX = re.compile(r"^[0-9a-f]{64}$")
SOURCES = (
    "official",
    "official_words",
    "official_md",
    "crosscheck",
    "td",
    "dev",
    "const",
    "meta",
)
# Which sources each section tag may quote (A6). Untagged sections may quote
# the official run, the cross-check file and the constants (provenance).
# ``official_words`` is the official results file under a second name. Only a
# [CROSS-CHECK] section may quote it: the table of differing verdict words
# there needs the official word beside the GPU word, while the source name
# ``official`` stays refused in that section (WU-0020.8, plan amendment).
ALLOWED = {
    "PRE-REGISTERED": {"official", "official_md", "const", "meta"},
    "DIAGNOSTIC": {"official", "const", "meta"},
    "CROSS-CHECK": {"crosscheck", "official_words", "td", "const", "meta"},
    "DEVELOPMENT": {"dev", "const", "meta"},
    "STUDENT": set(),
    "": {"official", "official_md", "crosscheck", "const", "meta"},
}
TD_ROW = re.compile(
    r"^\s+(\w+)\s+(H\d[a-z]\S*(?: (?:zero|interior))?)"
    r"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$"
)
TD_TOTALS = re.compile(
    r"parts computed (\S+) of (\S+) expected .*?sum z\^2 away (\S+), "
    r"symmetric \(information\) (\S+); max z away (\S+), symmetric "
    r"\(information\) (\S+); failing parts \(z_away > (\S+)\) (\S+)"
)
TD_DIFFERS = re.compile(r"^TD: (\d+) verdict-type leaves differ")
TD_RESULT = re.compile(r"^RESULT: (.*)$")
TD_TIER = re.compile(r"^tier: (\S+)")
TD_REF = re.compile(r"^REF: (.+)$")
TD_NEW = re.compile(r"^NEW: (.+)$")
TD_LEAF = re.compile(r"^      (\S+): (.+) -> (.+)$")


class ToolError(Exception):
    """An unreadable input or a usage error (exit code 2)."""


class Missing(KeyError):
    """A leaf path that is not in a source."""


@dataclass
class Row:
    """One quoted value: where it came from and how it was written.

    Attributes
    ----------
    source, path, spec : str
        The source name, the leaf path and the format.
    raw, rendered : str
        ``repr`` of the leaf and the string written into the document.
    tag : str
        The source tag of the section that holds the value.
    line, col : int
        Position of the rendered string in the document (line from 1).
    """

    source: str
    path: str
    spec: str
    raw: str
    rendered: str
    tag: str = ""
    line: int = 0
    col: int = 0


# --- reading leaves and formatting them ---------------------------------
def walk(tree: object, path: str) -> object:
    """Return the leaf at a ``/``-separated path (list items by index)."""
    node = tree
    for part in path.split("/"):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif (
            isinstance(node, list)
            and part.lstrip("-").isdigit()
            and -len(node) <= int(part) < len(node)
        ):
            node = node[int(part)]
        else:
            raise Missing(path)
    return node


def number_text(value: object, spec: str) -> str:
    """Format one number with a Python format spec; refuse non-numbers."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ToolError(f"format {spec!r} needs a number, got {value!r}")
    try:
        return format(value, spec)
    except ValueError as exc:
        raise ToolError(f"format {spec!r} cannot write {value!r}") from exc


def fmt(value: object, spec: str) -> str:
    """Write a leaf as text, deterministically.

    ``""`` copies a string or integer, ``yn`` writes a boolean as yes or no,
    ``verdict`` copies a verdict word and adds the required "(preliminary,
    unpromoted)" to "supported", ``ci:<spec>`` writes a two-number interval,
    and any other spec is a Python number format such as ``.3g``. A null leaf
    is written "not computed".
    """
    if value is None:
        return NOT_COMPUTED
    if spec == "yn":
        if not isinstance(value, bool):
            raise ToolError(f"format yn needs a boolean, got {value!r}")
        return "yes" if value else "no"
    if spec in ("", "verdict"):
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise ToolError(f"format {spec!r} needs text, got {value!r}")
        if spec == "verdict" and value == "supported":
            return "supported (preliminary, unpromoted)"
        return str(value)
    if spec.startswith("ci:"):
        if not isinstance(value, list) or len(value) != 2:
            raise ToolError(f"format {spec!r} needs a pair, got {value!r}")
        lo, hi = (number_text(v, spec[3:]) for v in value)
        return f"[{lo}, {hi}]"
    return number_text(value, spec)


def sha256_of(path: Path) -> str:
    """Return the SHA-256 of a file as hex."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    """Read a JSON file or raise ``ToolError``."""
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot read {path}: {exc}") from None


def split_cells(line: str) -> list[str]:
    """Split a Markdown table row on pipes that are not escaped."""
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def parse_results_md(path: Path) -> dict:
    """Read the banner, interval labels and clip cells of ``RESULTS.md``.

    These three are copied verbatim into the document, so the tool never
    rebuilds them: ``banner`` is the label line of ``report.header_lines``,
    ``label[id]`` is the line of the interval-label list, ``clip[id]`` is the
    last cell of the verdict-table row.
    """
    out: dict = {"banner": None, "label": {}, "clip": {}}
    lines = path.read_text().splitlines()
    out["banner"] = next((x for x in lines[1:6] if x.startswith("**")), None)
    in_labels = in_verdicts = False
    for line in lines:
        if line.startswith("Interval labels, one per row"):
            in_labels = True
        elif in_labels and line.startswith("## "):
            in_labels = False
        elif in_labels and line.startswith("- ") and " — " in line:
            key = line[2:].split(" — ")[0].split(" (")[0]
            key = "gain_bound" if key == "(reported)" else key
            out["label"][key] = line[2:]
        if line.startswith("| ID | Hypothesis |"):
            in_verdicts = True
        elif in_verdicts and not line.startswith("|"):
            in_verdicts = False
        elif in_verdicts and "---" not in line:
            cells = split_cells(line)
            key = "gain_bound" if cells[0] == "(reported)" else cells[0]
            out["clip"][key] = cells[-1]
    return out


def parse_td(path: Path) -> dict:
    """Read the TD table of a ``compare_runs`` text as printed strings.

    Every number stays the string that ``compare_runs`` printed, so the
    document copies it exactly (A10). ``compare_runs`` prints the count of
    differing verdict-type leaves only when it is nonzero, so an absent line
    is written as text, never as a number: "none listed" for a TD report and
    "not available" for any other text.
    """
    out: dict = {"parts": {}, "total": {}, "leaves": []}
    tier = None
    listing = False
    for line in path.read_text().splitlines():
        leaf = TD_LEAF.match(line) if listing else None
        if leaf:
            out["leaves"].append(leaf.groups())
            continue
        listing = bool(TD_DIFFERS.match(line))
        for key, regex in (("ref", TD_REF), ("new", TD_NEW)):
            found = regex.match(line)
            if found:
                out["total"][key] = found.group(1).strip()
        row = TD_ROW.match(line)
        if row:
            names = ("d", "z_sym", "z_away", "hw", "status")
            system, part = row.group(1), row.group(2)
            out["parts"].setdefault(system, {})[part] = dict(
                zip(names, row.groups()[2:])
            )
        found = TD_TIER.match(line)
        tier = found.group(1) if found else tier
        for regex, names in (
            (
                TD_TOTALS,
                (
                    "computed",
                    "expected",
                    "sum_away",
                    "sum_sym",
                    "max_away",
                    "max_sym",
                    "bound",
                    "failing",
                ),
            ),
            (TD_DIFFERS, ("differing",)),
            (TD_RESULT, ("result",)),
        ):
            hit = regex.search(line)
            if hit:
                out["total"].update(zip(names, hit.groups()))
    if "failing" not in out["total"]:
        raise ToolError(f"{path} has no TD totals line (not a TD report)")
    if "ref" not in out["total"] or "new" not in out["total"]:
        raise ToolError(f"{path} has no REF and NEW lines: refused")
    out["total"].setdefault(
        "differing", NONE_LISTED if tier == "TD" else NOT_AVAILABLE
    )
    out["total"]["listed"] = str(len(out["leaves"]))
    return out


def const_citation(tree: dict, path: str) -> str | None:
    """Return the ``v3`` citation of the deepest entry on a constant path."""
    node, found = tree, None
    for part in path.split("/"):
        node = walk(node, part)
        if isinstance(node, dict) and "v3" in node:
            found = node["v3"]
    return found


def is_word_key(key: str) -> bool:
    """Return True if a string leaf with this key holds a verdict word.

    The rule of ``tools/compare_runs.py`` for a verdict-type string leaf, typed
    again here (a test compares the two): ``verdict``, ``verdict_2L``,
    ``part_i_verdict``, ``reading`` and ``status``.
    """
    return (
        key.startswith("verdict")
        or key.endswith("_verdict")
        or key in ("reading", "status")
    )


def string_leaves(tree: object, prefix: tuple = ()) -> list[tuple]:
    """Return ``(path, text)`` for every string leaf of a nested dict or list."""
    if isinstance(tree, dict):
        return [
            leaf
            for k, v in tree.items()
            for leaf in string_leaves(v, prefix + (k,))
        ]
    if isinstance(tree, list):
        return [
            leaf
            for i, v in enumerate(tree)
            for leaf in string_leaves(v, prefix + (str(i),))
        ]
    return [(prefix, tree)] if isinstance(tree, str) else []


def differing_words(
    official: dict, cross: dict, constants: dict
) -> tuple[list[tuple], list[tuple]]:
    """List the stored verdict words that differ between two results files.

    A string comparison of stored leaves and nothing else (A3): the words
    are those under ``verdicts`` and the string leaves of ``systems`` whose
    key ``is_word_key``. A word that exists in one file only counts as
    different. Returns ``(overall, per_system)`` as lists of path tuples. The
    overall list holds the paths under ``verdicts``, the primary hypotheses
    first. The per-system list is ordered by system, then primary parts (the
    blocks of the primary rows) before the rest, then by path.
    """
    seen: dict[tuple, list] = {}
    for side, tree in enumerate((official, cross)):
        part = {k: tree[k] for k in ("verdicts", "systems") if k in tree}
        for path, word in string_leaves(part):
            if path[0] == "verdicts" or is_word_key(path[-1]):
                seen.setdefault(path, [None, None])[side] = word
    differ = [path for path, (a, b) in seen.items() if a != b]
    keys = [i["key"] for i in constants["identifiers"]]
    primary = {
        i["key"] for i in constants["identifiers"] if i["role"] == "primary"
    }
    rows = {p["row"] for p in constants["primary_parts"]}
    systems = list(constants["systems"])

    def overall_rank(path: tuple) -> tuple:
        key = path[1] if len(path) > 1 else ""
        return (
            0 if key in primary else 1,
            keys.index(key) if key in keys else len(keys),
            path,
        )

    def system_rank(path: tuple) -> tuple:
        system = path[1] if len(path) > 1 else ""
        block = path[2] if len(path) > 2 else ""
        return (
            systems.index(system) if system in systems else len(systems),
            system,
            0 if block in rows else 1,
            path,
        )

    overall = sorted(
        (p for p in differ if p[0] == "verdicts"), key=overall_rank
    )
    per_system = sorted(
        (p for p in differ if p[0] != "verdicts"), key=system_rank
    )
    return overall, per_system


# --- the document builder ---------------------------------------------
class Builder:
    """Fill the template and keep the trace of every quoted value.

    A quoted value is written as a marker (``\\x00id\\x01text\\x02``) while the
    text is assembled. ``finalize`` removes the markers and records each
    value's position, so the trace says exactly where every number sits.
    The systems are the three of v3 (a constant); a system that is absent
    from the results reads "not recorded" everywhere and counts as failing
    the gate, so no table shrinks silently.
    """

    def __init__(
        self, sources: dict, constants: dict, directory: Path, stem: str
    ):
        self.sources = sources
        self.meta = sources["meta"]
        self.constants = constants
        self.directory = directory
        self.stem = stem
        self.rows: list[Row] = []
        self.missing: list[str] = []
        self.nulls: list[str] = []
        self.counter = 0
        self.systems = list(constants["systems"])
        self.provisional = {
            s: self.gate_state("official", s) is not True for s in self.systems
        }

    def gate_state(self, source: str, system: str) -> object:
        """Return the stored ``gate_pass`` of a system (None if absent)."""
        try:
            return walk(
                self.sources[source],
                f"systems/{system}/validation/gate/gate_pass",
            )
        except Missing:
            return None

    def ref(self, source: str, path: str, spec: str = "") -> str:
        """Quote one leaf and record it; a missing leaf is "not recorded"."""
        try:
            value = walk(self.sources[source], path)
            raw, text = repr(value), fmt(value, spec)
            if value is None:
                self.nulls.append(f"{source}:{path}")
        except Missing:
            raw, text = MISSING, NOT_RECORDED
            self.missing.append(f"{source}:{path}")
        self.rows.append(Row(source, path, spec, raw, text))
        return f"\x00{len(self.rows) - 1}\x01{text}\x02"

    def meta_ref(self, key: str, value: object) -> str:
        """Store a value computed by the builder and quote it."""
        self.meta[key] = value
        return self.ref("meta", key)

    def const(self, path: str) -> str:
        """Quote a design constant (a bare name means ``constants/<name>``)."""
        if "/" not in path:
            path = f"constants/{path}/text"
        return self.ref("const", path)

    def official(self, system: str, leaf: str, spec: str = "") -> str:
        """Quote a leaf of one system of the official run."""
        return self.ref("official", f"systems/{system}/{leaf}", spec)

    def mark(self, system: str) -> str:
        """Return the PROVISIONAL mark of a system whose gate did not pass."""
        return " PROVISIONAL" if self.provisional[system] else ""

    # --- tables -------------------------------------------------------
    def table(self, name: str) -> str:
        """Return the generated block called ``name``."""
        maker = getattr(self, f"table_{name}", None)
        if maker is None:
            raise ToolError(f"unknown table {name!r} in the template")
        return "\n".join(maker())

    def table_provenance(self) -> list[str]:
        """Provenance of both runs, from the stored provenance blocks."""
        rows = [
            ("Seed id", "official", "provenance/seed_id", ""),
            ("Seed kind", "official", "provenance/seed_kind", ""),
            ("Label", "official", "provenance/label", ""),
            ("Preset", "official", "provenance/preset", ""),
            ("Commit", "official", "provenance/commit", ""),
            ("Freeze check", "meta", "freeze_check", ""),
            ("Backend", "official", "provenance/device/backend", ""),
            ("LPC_THREADS", "official", "provenance/env/LPC_THREADS", ""),
            ("Dirty", "official", "provenance/dirty", "yn"),
            ("Complete", "official", "provenance/complete", "yn"),
            ("Wall seconds", "official", "provenance/wall_seconds", ".0f"),
            ("Start (UTC)", "official", "provenance/start_utc", ""),
            ("End (UTC)", "official", "provenance/end_utc", ""),
            ("SHA-256 of results.json", "meta", "official_sha", ""),
            ("SHA-256 of RESULTS.md", "meta", "official_md_sha", ""),
            ("Manifest hashes", "meta", "manifest_check", ""),
            ("Release reference", "meta", "release_ref", ""),
            ("Cross-check seed id", "crosscheck", "provenance/seed_id", ""),
            (
                "Cross-check backend",
                "crosscheck",
                "provenance/device/backend",
                "",
            ),
            ("Cross-check SHA-256", "meta", "crosscheck_sha", ""),
            ("compare_runs text", "meta", "td_binding", ""),
        ]
        out = ["| Item | Value |", "|---|---|"] + [
            f"| {name} | {self.ref(src, path, spec)} |"
            for name, src, path, spec in rows
        ]
        out.append(
            f"| Cross-check commit | "
            f"{self.ref('crosscheck', 'provenance/commit')} (same as "
            f"official: {self.ref('meta', 'cross_commit_same')}) |"
        )
        differs = self.ref("meta", "cross_commit_differs")
        return out + [
            "",
            "Cross-check commits that differ from the official commit: "
            f"{differs} (a later commit is allowed only if "
            "`git diff --name-only` shows paths under docs/agent/records/ or "
            f"the ledger alone; check: {self.ref('meta', 'cross_commit_check')}"
            "; both commits are shown above).",
        ]

    def table_gate(self) -> list[str]:
        """Gate V1 to V7 per system with each statistic and the pass flag."""
        out = [
            "| System | Check | Statistic | Value | Bar | Pass |",
            "|---|---|---|---|---|---|",
        ]
        for s in self.systems:
            for gate in self.constants["gate_rows"]:
                flag = (
                    "n/a"
                    if gate["pass"] is None
                    else self.official(s, gate["pass"], "yn")
                )
                for k, (label, leaf, spec) in enumerate(gate["stats"]):
                    first = k == 0
                    out.append(
                        f"| {s}{self.mark(s)} | {gate['check']} | {label} | "
                        f"{self.official(s, leaf, spec)} | "
                        f"{self.const(gate['bar']) if first else ''} | "
                        f"{flag if first else ''} |"
                    )
            overall = self.official(s, "validation/gate/gate_pass", "yn")
            out.append(
                f"| {s}{self.mark(s)} | gate | gate_pass | | | {overall} |"
            )
        return out

    def table_verdicts(self) -> list[str]:
        """The 14 identifier rows: per-system verdict, overall, clip text."""
        out = [
            "| ID | Role | " + " | ".join(self.systems) + " | Overall | clip |",
            "|---|---|" + "---|" * (len(self.systems) + 2),
        ]
        for item in self.constants["identifiers"]:
            key = item["key"]
            overall = self.ref("official", f"verdicts/{key}/verdict", "verdict")
            if key == "Q-N":
                # v3 section 2 and 7 read the two parts separately; the stored
                # overall word is built from the logit part alone (R1).
                cells = [self.qn_cell(s) + self.mark(s) for s in self.systems]
                overall += (
                    "; the stored per-system words are the logit part only"
                )
            else:
                cells = [
                    self.ref(
                        "official", f"verdicts/{key}/by_system/{s}", "verdict"
                    )
                    + self.mark(s)
                    for s in self.systems
                ]
            out.append(
                f"| {key} | {item['role']} | {' | '.join(cells)} | "
                f"{overall} | {self.ref('official_md', f'clip/{key}')} |"
            )
        return out

    def qn_cell(self, system: str) -> str:
        """Both stored Q-N readings of a system: the logit and the indicator."""
        logit, indicator = self.constants["qn_parts"][:2]
        return (
            f"logit: {self.official(system, logit['verdict'])}; "
            f"indicator: {self.official(system, indicator['verdict'])}"
        )

    def parts_rows(
        self, parts_key: str, default_level: str, notes: bool
    ) -> list[str]:
        """Rows of a parts table: estimate, interval, level, band, verdict.

        The level is the stored leaf where the results have one. Otherwise it
        is the design level of v3 section 7, written with the words "design
        value, not stored", and those cells are counted under the table.
        """
        head = ["System", "Part", "Estimate", "Interval", "Level", "Band"]
        head += ["Verdict"] + (["Notes"] if notes else [])
        out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        designed = 0
        for s in self.systems:
            for i, part in enumerate(self.constants[parts_key]):
                level = part["level"]
                if level and self.has_leaf(s, level):
                    level_cell = self.official(s, level, ".4f")
                else:
                    designed += 1
                    level_cell = (
                        f"{self.const(default_level)} "
                        f"({self.const('level_design_note')})"
                    )
                spec = (
                    ""
                    if part["verdict"].endswith(("reading", "role"))
                    else "verdict"
                )
                cells = [
                    f"{s}{self.mark(s)}",
                    part["name"],
                    self.official(s, part["estimate"], ".4g"),
                    self.official(s, part["interval"], "ci:.4g"),
                    level_cell,
                    self.const(f"{parts_key}/{i}/band_text"),
                    self.official(s, part["verdict"], spec),
                ]
                if notes:
                    cells.append(
                        f"{self.const('lm_note')}; {self.const('block_note')}"
                    )
                out.append("| " + " | ".join(cells) + " |")
        self.counter += 1
        count = self.meta_ref(f"design_levels_{self.counter}", str(designed))
        out += ["", f"Level cells that show a design value: {count}."]
        if notes:
            out += [
                "",
                "Iterative error of the PLP estimator: not estimated for this "
                "run. Development evidence is in "
                f"{self.const('lm_report_pointer')} and in the limitation on "
                "iterative error (DEF-0027) in §10.",
            ]
        return out

    def has_leaf(self, system: str, leaf: str) -> bool:
        """Return True if a leaf of the official run exists."""
        try:
            walk(self.sources["official"], f"systems/{system}/{leaf}")
            return True
        except Missing:
            return False

    def table_primary(self) -> list[str]:
        """The 18 primary parts (6 parts times 3 systems)."""
        return self.parts_rows("primary_parts", "primary_level", True)

    def table_secondary(self) -> list[str]:
        """Secondary parts with their intervals."""
        return self.parts_rows("secondary_parts", "standard_level", False)

    def table_qn(self) -> list[str]:
        """Q-N parts: the interval of the gain in R squared and its reading."""
        return self.parts_rows("qn_parts", "standard_level", False)

    def table_h3a(self) -> list[str]:
        """H3a states, events and censored states per regime, and p-values."""
        out = [
            "| System | Regime | States | Events | Censored |",
            "|---|---|---|---|---|",
        ]
        pairs = [
            "",
            "| System | Pair (a, b) | Raw p | Holm p |",
            "|---|---|---|---|",
        ]
        for s in self.systems:
            base = f"systems/{s}/H3a"
            for k in range(self.length(f"{base}/n_per_regime")):
                cells = [
                    self.ref("official", f"{base}/{leaf}/{k}", "d")
                    for leaf in (
                        "n_per_regime",
                        "n_events_per_regime",
                        "n_censored_per_regime",
                    )
                ]
                out.append(
                    f"| {s}{self.mark(s)} | r{k} | {' | '.join(cells)} |"
                )
            for k in range(self.length(f"{base}/pairs")):
                pair = ", ".join(
                    self.ref("official", f"{base}/pairs/{k}/{j}", "d")
                    for j in (0, 1)
                )
                raw = self.ref("official", f"{base}/logrank_p_raw/{k}", ".3g")
                holm = self.ref("official", f"{base}/logrank_p_holm/{k}", ".3g")
                pairs.append(f"| {s}{self.mark(s)} | {pair} | {raw} | {holm} |")
        return out + pairs

    def length(self, path: str) -> int:
        """Return the length of a stored list (0 if absent, and count it)."""
        try:
            return len(walk(self.sources["official"], path))
        except Missing:
            self.missing.append(f"official:{path}")
            return 0

    def table_counts(self) -> list[str]:
        """Say how many cells so far are "not recorded" or "not computed"."""
        self.counter += 1
        missing = self.meta_ref(
            f"missing_{self.counter}", str(len(self.missing))
        )
        nulls = self.meta_ref(f"nulls_{self.counter}", str(len(self.nulls)))
        return [
            f'Cells written "{NOT_RECORDED}" so far: {missing}. '
            f'Null leaves written "{NOT_COMPUTED}" so far: {nulls}. '
            "The full list is in Appendix C."
        ]

    def table_gain(self) -> list[str]:
        """The reported hybrid horizon gain against the P1 bound."""
        leaves = (
            ("fraction_within_bound", ".3f"),
            ("n_states", "d"),
            ("n_total_states", "d"),
            ("median_gain_lyapunov", ".3g"),
            ("max_gain_lyapunov", ".3g"),
        )
        out = [
            "| System | " + " | ".join(n for n, _ in leaves) + " |",
            "|---|" + "---|" * len(leaves),
        ]
        for s in self.systems:
            cells = " | ".join(
                self.official(s, f"gain_bound/{n}", spec) for n, spec in leaves
            )
            out.append(f"| {s}{self.mark(s)} | {cells} |")
        return out

    def table_handling(self) -> list[str]:
        """Every handling counter: run total and per-system counts."""
        totals = walk(self.sources["official"], "handling/totals")
        out = [
            "| Counter | Total | " + " | ".join(self.systems) + " |",
            "|---|---|" + "---|" * len(self.systems),
        ]
        for name in totals:
            cells = " | ".join(
                self.ref("official", f"handling/by_system/{s}/{name}", "d")
                for s in self.systems
            )
            out.append(
                f"| {name} | "
                f"{self.ref('official', f'handling/totals/{name}', 'd')} | "
                f"{cells} |"
            )
        failed = self.ref("official", "handling/failed_variants", "d")
        skipped = self.ref("official", "handling/skipped_variants", "d")
        return out + [
            "",
            f"Failed robustness variants: {failed}. Robustness variants not "
            f"run (skipped_variants): {skipped}.",
        ]

    def table_resultcounts(self) -> list[str]:
        """Counts of floors, exclusions and screen-outs, from their leaves."""
        out = [
            "| Result count (leaf of each system) | "
            + " | ".join(self.systems)
            + " |",
            "|---|" + "---|" * len(self.systems),
        ]
        for i, item in enumerate(self.constants["result_counts"]):
            cells = " | ".join(
                self.official(s, item["leaf"], "d") for s in self.systems
            )
            out.append(f"| {self.const(f'result_counts/{i}/leaf')} | {cells} |")
        return out

    def table_reported(self) -> list[str]:
        """Reported quantities with no verdict (R6), one row per system."""
        out = [
            "| System | Quantity | Value | Interval |",
            "|---|---|---|---|",
        ]
        for s in self.systems:
            for i, item in enumerate(self.constants["reported_quantities"]):
                value = self.official(s, item["leaf"], item["fmt"])
                interval = (
                    self.official(s, item["ci"], "ci:" + item["fmt"])
                    if "ci" in item
                    else ""
                )
                label = self.const(f"reported_quantities/{i}/label")
                out.append(
                    f"| {s}{self.mark(s)} | {label} | {value} | {interval} |"
                )
        return out

    def table_crosscheck(self) -> list[str]:
        """The TD table of the cross-check and its totals."""
        out = [
            "| System | Part | d | z_sym (information) | z_away (governs) | "
            "hw ratio | Status |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in self.systems:
            for part in self.constants["primary_parts"]:
                cells = " | ".join(
                    self.ref("td", f"parts/{s}/{part['name']}/{f}")
                    for f in ("d", "z_sym", "z_away", "hw", "status")
                )
                out.append(f"| {s}{self.mark(s)} | {part['name']} | {cells} |")
        total = lambda name: self.ref("td", f"total/{name}")  # noqa: E731
        out += [
            "",
            f"Parts computed {total('computed')} of {total('expected')}; "
            f"sum of z squared (away) {total('sum_away')}; "
            f"largest z (away) {total('max_away')}; "
            f"failing parts {total('failing')} (bound {self.const('td_bound')}).",
        ]
        return out

    def table_crossverdicts(self) -> list[str]:
        """Stored verdict words that differ between the two runs (R2).

        A string comparison of the stored words of the two results files
        (``differing_words``); no verdict is recomputed. Overall words come
        first, then the words of each system with the primary parts first.
        The regimes of H3a per system follow, because with a different
        number of regimes some H3a leaves exist in one run only.
        """
        overall, per_system = differing_words(
            self.sources["official"],
            self.sources["crosscheck"],
            self.constants,
        )
        total = lambda name: self.ref("td", f"total/{name}")  # noqa: E731
        n_overall = self.meta_ref("cross_words_overall", str(len(overall)))
        n_system = self.meta_ref("cross_words_system", str(len(per_system)))
        out = [
            "Stored verdict words that differ between the official (CPU) and "
            "the cross-check (GPU) results files, read from the two files as "
            "a string comparison of the stored words (nothing is "
            f"recomputed). Overall rows: {n_overall}. Rows per system: "
            f"{n_system}. The compare_runs text prints a limited number of "
            f"leaf lines ({total('listed')} lines against {total('differing')} "
            "verdict-type leaves counted, which also include boolean flags of "
            "the verdict rows); the tables below are read from the results "
            "files and list every string verdict word that differs.",
            "",
        ]
        words = lambda path: (  # noqa: E731
            f"{self.ref('official_words', '/'.join(path), 'verdict')} | "
            f"{self.ref('crosscheck', '/'.join(path), 'verdict')}"
        )
        if overall:
            out += [
                "| Overall leaf | Official (CPU) | Cross-check (GPU) |",
                "|---|---|---|",
            ]
        else:
            out += ["No overall stored verdict word differs.", ""]
        for k, path in enumerate(overall):
            label = self.meta_ref(f"cross_label_o{k}", "/".join(path[1:]))
            system = path[3] if len(path) > 3 and path[2] == "by_system" else ""
            mark = self.mark(system) if system in self.provisional else ""
            out.append(f"| {label}{mark} | {words(path)} |")
        out.append("")
        if per_system:
            out += [
                "| System | Leaf | Official (CPU) | Cross-check (GPU) |",
                "|---|---|---|---|",
            ]
        else:
            out += ["No stored verdict word of a system differs.", ""]
        for k, path in enumerate(per_system):
            label = self.meta_ref(f"cross_label_s{k}", "/".join(path[2:]))
            mark = self.mark(path[1]) if path[1] in self.provisional else ""
            out.append(f"| {path[1]}{mark} | {label} | {words(path)} |")
        out += [
            "",
            "H3a regimes per system (the stored chosen_K of each run). When "
            "the numbers differ, the regime-indexed H3a leaves of the longer "
            "list have no counterpart in the other run; compare_runs lists "
            "them with no per-leaf rule.",
            "",
            "| System | Regimes, official (CPU) | Regimes, cross-check (GPU) |",
            "|---|---|---|",
        ]
        for s in self.systems:
            first = self.ref("official_words", f"systems/{s}/H3a/chosen_K", "d")
            second = self.ref("crosscheck", f"systems/{s}/H3a/chosen_K", "d")
            out.append(f"| {s}{self.mark(s)} | {first} | {second} |")
        return out

    def table_labels(self) -> list[str]:
        """Interval labels copied from RESULTS.md, one per identifier."""
        return [
            "- " + self.ref("official_md", f"label/{item['key']}")
            for item in self.constants["identifiers"]
        ]

    # --- text blocks --------------------------------------------------
    def stored_word(self, source: str, path: str) -> object:
        """Return the stored leaf (None if it is absent or null)."""
        try:
            return walk(self.sources[source], path)
        except Missing:
            return None

    def overall_bullet(self, key: str, label: str) -> str:
        """One bullet: the stored overall word and the wording for that word.

        The sentence is picked by looking the stored word up (a table of
        sentences); nothing is compared with a band.
        """
        wording = self.constants["wording"]
        path = f"verdicts/{key}/verdict"
        word = self.stored_word("official", path)
        text = wording.get(word, NOT_RECORDED) if word else NOT_RECORDED
        if word == "not supported" and f"reading:{key}" in wording:
            text += " " + wording[f"reading:{key}"]
        if key == "H2a":
            text += (
                f" Parts whose stored word is fail: {self.failed_parts(key)}. "
                f"Precision (v3 §7, DEF-0022): {self.const('precision_h2a')}"
            )
        return f"- **{label}**: {self.ref('official', path, 'verdict')}. {text}"

    def failed_parts(self, row: str) -> str:
        """Name, per system, the parts of a row whose stored word is fail.

        A part whose leaf is absent or null is named too (with the words
        "not recorded" or "not computed"), because its word is not known.
        """
        out = []
        for s in self.systems:
            names = []
            for part in self.constants["primary_parts"]:
                if part["row"] != row:
                    continue
                word = self.stored_word(
                    "official", f"systems/{s}/{part['verdict']}"
                )
                if word is None or word == "fail":
                    cell = self.official(s, part["verdict"], "verdict")
                    names.append(f"{part['name']} ({cell})")
            out.append(f"{s}{self.mark(s)}: {', '.join(names) or 'none'}")
        return "; ".join(out)

    def wording_primary(self) -> str:
        """Bullets of the three primary rows (R7)."""
        lines = ["Primary hypotheses, stored overall words:"]
        lines += [
            self.overall_bullet(key, key) for key in ("H2a", "H2b", "H3c")
        ]
        return "\n".join(lines)

    def wording_secondary(self) -> str:
        """Bullets of the secondary rows that are poster highlights (R8)."""
        intro = self.constants["wording"]["secondary_intro"].format(
            level=self.const("standard_level_pct")
        )
        lines = [intro]
        lines += [
            self.overall_bullet(key, f"{key} (secondary)")
            for key in ("H2c", "H2e", "H3a")
        ]
        return "\n".join(lines)

    def wording_qn(self) -> str:
        """The Q-N sentence: two parts, and the stored overall word (R1)."""
        words = ", ".join(
            f"{s} {self.ref('official', f'verdicts/Q-N/by_system/{s}')}"
            f"{self.mark(s)}"
            for s in self.systems
        )
        return (
            "Q-N is read by the table of v3 §7, separately for each of its two "
            "parts (logit w* on the interior states, and the indicator of w* "
            "at zero), and is never pass or fail; the Q-N row shows both "
            "stored readings. v3 §2 and §7 read the two parts separately, but "
            "the stored overall word `verdicts.Q-N` collapses them to the "
            f"logit part: its per-system words are {words}."
        )

    def wording_h2c_label(self) -> str:
        """Explain the H2c label "A4 - A1" (stored best_single) (R6)."""
        best = ", ".join(
            f"{s}{self.mark(s)} {self.official(s, 'H2c/best_single')}"
            for s in self.systems
        )
        return (
            "The H2c part labelled A4 - A1 is A4 minus the better single "
            "forecaster, chosen on the calibration split (v3 §2 H2c). The "
            f"stored best_single is {best}; {self.const('a1_is_plp')}."
        )

    def wording_gpu(self) -> str:
        """One sentence per cross-check condition, each as stored (R3).

        The conditions are the largest z against the bound, the number of
        differing verdict-type leaves and the GPU gate of each system. The
        sentence of a condition is picked by a string comparison of the
        stored token (failing parts "0" or not; gate_pass true or not); an
        unavailable count is printed as such and cannot read as agreement.
        """
        wording = self.constants["wording"]
        total = self.sources["td"]["total"]
        token = lambda name: self.ref("td", f"total/{name}")  # noqa: E731
        bound_key = (
            "gpu_bound_ok" if total["failing"] == "0" else "gpu_bound_exceeded"
        )
        bound = wording[bound_key].format(
            failing=token("failing"),
            max_away=token("max_away"),
            bound=self.const("td_bound"),
        )
        differing = wording["gpu_diff_count"].format(
            differing=token("differing")
        )
        gates = {s: self.gate_state("crosscheck", s) for s in self.systems}
        listing = ", ".join(
            f"{s} "
            + self.ref(
                "crosscheck", f"systems/{s}/validation/gate/gate_pass", "yn"
            )
            for s in self.systems
        )
        failed = [s for s, g in gates.items() if g is not True]
        gate = (
            wording["gpu_gate_failed"].format(systems=", ".join(failed))
            if failed
            else wording["gpu_gate_ok"]
        )
        result = wording["gpu_result"].format(
            result=token("result"), dec28=self.const("dec28_item4")
        )
        return "\n\n".join(
            [
                bound,
                differing,
                f"GPU validation gate, stored gate_pass: {listing}. {gate}",
                f"{result} {wording['gpu_info_only']}",
            ]
        )

    def gate_box(self) -> str:
        """The boxed gate sentence: failure branch or all-clear branch."""
        wording = self.constants["wording"]
        failed = any(self.provisional.values())
        return "> " + wording["gate_failure" if failed else "gate_ok"]

    def dev_appendix(self) -> str:
        """The development appendix: verdict words of a development run."""
        if "dev" not in self.sources:
            return (
                "No development appendix in this build. Development-seed "
                "numbers appear only here, labeled, and never beside the "
                "official result (owner ruling D4). A development ensemble "
                "may be appended later."
            )
        keys = [i["key"] for i in self.constants["identifiers"]]
        out = [
            "Development seed numbers are not a hypothesis test and say "
            "nothing about the official result. Stored verdict words of the "
            "development run:",
            "",
            "| ID | " + " | ".join(self.systems) + " |",
            "|---|" + "---|" * len(self.systems),
        ]
        for key in keys:
            cells = " | ".join(
                self.ref("dev", f"verdicts/{key}/by_system/{s}", "verdict")
                for s in self.systems
            )
            out.append(f"| {key} | {cells} |")
        return "\n".join(out)

    def figure(self, name: str) -> str:
        """Draw figure ``name`` (F1 to F3) and return its Markdown block."""
        figures = self.directory / f"{self.stem}.figures"
        figures.mkdir(parents=True, exist_ok=True)
        label = walk(self.sources["official"], "provenance/label")
        files = {
            "F1": "F1_primary",
            "F2": "F2_secondary",
            "F3": "F3_crosscheck",
        }
        marks = dict(self.provisional)
        if name == "F3":
            gates = {s: self.gate_state("crosscheck", s) for s in self.systems}
            fig = draw_crosscheck(
                self.sources["td"], self.constants, label, marks, gates
            )
        else:
            key = "primary_parts" if name == "F1" else "secondary_parts"
            parts = self.constants[key]
            parts = parts + (self.constants["qn_parts"] if name == "F2" else [])
            panels = panel_data(
                self.sources["official"], parts, self.systems, self.constants
            )
            fig = draw_panels(panels, 3 if name == "F1" else 5, label, marks)
        save_figure(fig, figures / f"{files[name]}.png")
        link = self.meta_ref(
            f"figure_{name}", f"{self.stem}.figures/{files[name]}.png"
        )
        return f"![{name}]({link})\n\n*{self.const('caption_' + name)}*"

    def missing_note(self) -> str:
        """Count and list the leaves that were not found (PRIME.4)."""
        unique = sorted(set(self.missing))
        self.meta["missing_paths"] = unique
        count = self.meta_ref("missing_total", str(len(unique)))
        nulls = self.meta_ref("nulls_total", str(len(set(self.nulls))))
        text = [
            f'Leaves not found in the sources, written "{NOT_RECORDED}": '
            f'{count}. Null leaves written "{NOT_COMPUTED}": {nulls}.'
        ]
        text += [
            f"- {self.ref('meta', f'missing_paths/{k}')}"
            for k in range(len(unique))
        ]
        return "\n".join(text)

    def expand(self, template: str) -> str:
        """Replace every placeholder of the template, in order."""
        simple = {
            "gate_box": self.gate_box,
            "dev_appendix": self.dev_appendix,
        }

        def replace(match: re.Match) -> str:
            kind, arg, spec = match.group(1), match.group(2), match.group(3)
            if kind == "const":
                return self.const(arg)
            if kind in SOURCES:
                return self.ref(kind, arg, spec or "")
            if kind == "table":
                if arg == "missing":
                    return self.missing_note()
                return self.table(arg)
            if kind == "fig":
                return self.figure(arg)
            if kind == "wording":
                return getattr(self, f"wording_{arg}")()
            if kind == "banner":
                return self.ref("official_md", "banner")
            if kind == "mode_notice":
                return self.meta["mode_notice"]
            if kind in simple:
                return simple[kind]()
            raise ToolError(f"unknown placeholder {match.group(0)!r}")

        return PLACEHOLDER.sub(replace, template)

    def finalize(self, text: str) -> str:
        """Remove the markers, record the positions and the section tags."""
        out, pos, line, col = [], 0, 1, 0
        for match in MARK.finditer(text):
            piece = text[pos : match.start()]
            out.append(piece)
            line += piece.count("\n")
            col = (
                len(piece) - piece.rfind("\n") - 1
                if "\n" in piece
                else col + len(piece)
            )
            row = self.rows[int(match.group(1))]
            row.line, row.col = line, col
            out.append(match.group(2))
            col += len(match.group(2))
            pos = match.end()
        out.append(text[pos:])
        final = "".join(out)
        tags = section_tags(final)
        for row in self.rows:
            row.tag = tags[row.line - 1]
        return final


def section_tags(text: str) -> list[str]:
    """Return the source tag of each line (from the nearest ``##`` heading)."""
    tags, current = [], ""
    for line in text.split("\n"):
        head = HEADING.match(line)
        if head:
            tag = TAG.search(line)
            if tag:
                current = tag.group(1)
            elif head.group(1) == "##":
                current = ""
        tags.append(current)
    return tags


# --- figures ----------------------------------------------------------
OKABE = {"pass": "#009E73", "fail": "#D55E00", "inconclusive": "#0072B2"}
OKABE_OTHER = "#CC79A7"
BAND_COLOR = "#56B4E9"
MARKERS = {"pass": "o", "fail": "X", "inconclusive": "D"}


def panel_data(
    official: dict, parts: list[dict], systems: list[str], constants: dict
) -> list[dict]:
    """Collect the stored estimate, interval and verdict of each panel.

    Returns one dict per panel with ``name``, ``experiment``, ``band``,
    ``lines`` (reference lines, drawn instead of a band), ``level`` (text),
    ``systems`` and ``points`` (one entry per system: ``(est, lo, hi, label)``,
    or the text "not recorded" or "not computed"). A part marked ``own_axis``
    gets one panel per system, because the systems' scales differ too much to
    share an axis. The numbers are the leaves as stored: nothing is
    recomputed.
    """
    panels = []
    for part in parts:
        default = (
            "primary_level"
            if part in constants["primary_parts"]
            else "standard_level"
        )
        groups = [[s] for s in systems] if part.get("own_axis") else [systems]
        for group in groups:
            points, levels = [], []
            for s in group:
                base = f"systems/{s}/"
                try:
                    est = float(walk(official, base + part["estimate"]))
                    lo, hi = (
                        float(v)
                        for v in walk(official, base + part["interval"])
                    )
                    label = str(walk(official, base + part["verdict"]))
                    points.append((est, lo, hi, label))
                except Missing:
                    points.append(NOT_RECORDED)
                except TypeError:
                    points.append(NOT_COMPUTED)
                try:
                    levels.append(
                        float(walk(official, base + str(part["level"])))
                    )
                except (Missing, TypeError, ValueError):
                    pass
            level = (
                f"{levels[0]:.4f}"
                if levels
                else constants["constants"][default]["text"] + " (design value)"
            )
            name = part["name"] + (f" {group[0]}" if len(group) == 1 else "")
            panels.append(
                {
                    "name": name,
                    "experiment": part["experiment"],
                    "band": part["band"],
                    "lines": part.get("lines", []),
                    "level": level,
                    "systems": group,
                    "points": points,
                }
            )
    return panels


def status_title(label: str) -> str:
    """Return the figure title: the provenance label and the status line."""
    return f"{label}\n{PRELIMINARY_LINE}"


def draw_panels(
    panels: list[dict], columns: int, label: str, provisional: dict
) -> plt.Figure:
    """Draw one small panel per part: markers, interval bars and band.

    Marker shape and text carry the verdict, so color is never the only cue.
    A system that failed the validation gate is named PROVISIONAL on its
    row of every panel. A part with reference lines (Q-N) gets dashed lines
    at the reading edges and no shaded band, since a reading is not a pass.
    """
    rows = -(-len(panels) // columns)
    fig, axes = plt.subplots(
        rows, columns, figsize=(4.2 * columns, 2.3 * rows + 1.0), squeeze=False
    )
    for ax in axes.flat[len(panels) :]:
        ax.axis("off")
    for ax, panel in zip(axes.flat, panels):
        names = panel["systems"]
        ends = [
            v for p in panel["points"] if isinstance(p, tuple) for v in p[1:3]
        ]
        ends += [b for b in panel["band"] if b is not None] + panel["lines"]
        low, high = (min(ends), max(ends)) if ends else (0.0, 1.0)
        pad = 0.08 * (high - low or 1.0)
        low, high = low - pad, high + pad
        if any(b is not None for b in panel["band"]):
            lo_edge = low if panel["band"][0] is None else panel["band"][0]
            hi_edge = high if panel["band"][1] is None else panel["band"][1]
            ax.axvspan(lo_edge, hi_edge, color=BAND_COLOR, alpha=0.2, lw=0)
        for edge in panel["lines"]:
            ax.axvline(edge, color="#555555", ls="--", lw=0.8)
        for y, point in enumerate(panel["points"]):
            if not isinstance(point, tuple):
                ax.text(low, y, f" {point}", va="center", fontsize=7)
                continue
            est, lo, hi, word = point
            color = OKABE.get(word, OKABE_OTHER)
            ax.plot([lo, hi], [y, y], color=color, lw=1.5)
            ax.plot(
                [est],
                [y],
                marker=MARKERS.get(word, "s"),
                color=color,
                markerfacecolor="none" if word == "inconclusive" else color,
                ms=6,
                ls="",
            )
            ax.annotate(
                word,
                (est, y),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                fontsize=6,
            )
        ax.set_xlim(low, high)
        ax.set_ylim(-0.6, len(names) - 0.4)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(
            [n + (" PROVISIONAL" if provisional[n] else "") for n in names],
            fontsize=7,
        )
        # Few ticks and a shared power of ten: panels with a tiny range
        # (differences of 1e-5) printed overlapping labels (R9).
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.ticklabel_format(
            axis="x", style="sci", scilimits=(-2, 3), useOffset=False
        )
        ax.tick_params(axis="x", labelsize=7)
        ax.set_title(
            f"{panel['name']} ({panel['experiment']})\nlevel {panel['level']}",
            fontsize=7,
        )
    fig.suptitle(status_title(label), fontsize=8)
    fig.tight_layout()
    return fig


def crosscheck_points(
    td: dict, constants: dict
) -> list[tuple[str, str, float]]:
    """Return ``(system, part, z_away)`` for every parsed TD row."""
    points = []
    for system in constants["systems"]:
        for part in constants["primary_parts"]:
            row = td["parts"].get(system, {}).get(part["name"])
            if row:
                points.append((system, part["name"], float(row["z_away"])))
    return points


def draw_crosscheck(
    td: dict, constants: dict, label: str, provisional: dict, gpu_gate: dict
) -> plt.Figure:
    """Draw the cross-check z values, in gray, with the bound line.

    Each row names its system's PROVISIONAL status, and a system whose GPU
    validation gate failed (or is not recorded) is named in the row and in
    the footer.
    """
    points = crosscheck_points(td, constants)
    fig, ax = plt.subplots(figsize=(7.0, 0.3 * len(points) + 2.0))
    ys = list(range(len(points)))
    ax.plot([z for _, _, z in points], ys, "o", color="#555555")
    bound = float(constants["constants"]["td_bound"]["text"])
    ax.axvline(bound, color="#555555", ls="--")
    names = []
    for system, part, _ in points:
        extra = " PROVISIONAL" if provisional[system] else ""
        extra += (
            " [GPU gate not passed]" if gpu_gate[system] is not True else ""
        )
        names.append(f"{system} {part}{extra}")
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("z (away arm)")
    ax.set_title("Cross-check, information only", fontsize=9)
    gate_text = ", ".join(
        f"{s} {'passed' if gpu_gate[s] is True else 'NOT passed'}"
        for s in constants["systems"]
    )
    fig.suptitle(status_title(label), fontsize=8)
    fig.text(0.01, 0.01, f"GPU validation gate: {gate_text}", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def save_figure(fig: plt.Figure, path: Path) -> None:
    """Save a PNG with no timestamp or software tag (byte-identical reruns)."""
    fig.savefig(path, dpi=130, metadata={"Software": None})
    plt.close(fig)


# --- sources, guard and render -------------------------------------------
def banner_rule(provenance: dict) -> str:
    """Return the label line as ``report.header_lines`` writes it (A1)."""
    label = provenance["label"]
    return (
        f"**{label}**"
        if "UNPROMOTED" in label
        else f"**{label}** · **UNPROMOTED**"
    )


def git_freeze_commit(root: Path) -> str:
    """Return ``git rev-parse freeze-1^{commit}`` or raise ``ToolError``."""
    done = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "freeze-1^{commit}"],
        capture_output=True,
        text=True,
    )
    if done.returncode:
        raise ToolError("cannot resolve freeze-1: " + done.stderr.strip())
    return done.stdout.strip()


def git_changed_paths(root: Path, old: str, new: str) -> list[str]:
    """Return the paths changed from ``old`` to ``new`` (read-only git).

    Runs ``git diff --no-renames --no-ext-diff --no-textconv --name-only -z
    old..new``. ``--no-renames`` matters: with renames detected (git's
    default) ``--name-only`` lists only the destination of a moved file, so a
    move out of ``lpcstudy/`` into the records would look like a records
    change. Raises ``ToolError`` when git cannot answer (a missing commit, no
    repository, no git) or prints a path that is not valid UTF-8.
    """
    try:
        done = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "diff",
                "--no-renames",
                "--no-ext-diff",
                "--no-textconv",
                "--name-only",
                "-z",
                f"{old}..{new}",
            ],
            capture_output=True,
        )
    except OSError as exc:
        raise ToolError(f"cannot run git: {exc}") from None
    if done.returncode:
        raise ToolError(
            f"git cannot list the paths changed between {old} and {new}: "
            + done.stderr.decode("utf-8", "replace").strip()
        )
    paths = []
    for raw in done.stdout.split(b"\0"):
        try:
            paths.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            raise ToolError(
                f"git lists a path that is not valid UTF-8 ({raw!r}): refused"
            ) from None
    return [x for x in paths if x]


def check_later_commit(root: Path, official: object, cross: object) -> str:
    """Refuse a cross-check commit that changes more than records (N2).

    Both commits must be 40 hex digits. Every path that
    ``git diff --no-renames --name-only <official>..<cross-check>`` lists
    (the old and the new path of a move) must lie under
    ``docs/agent/records/`` or be ``docs/agent/governance/ledger.jsonl``, and
    none may contain a ``..`` component. Returns the sentence for the
    document; raises ``ToolError`` otherwise.
    """
    for commit in (official, cross):
        if not FULL_COMMIT.fullmatch(str(commit)):
            raise ToolError(
                f"commit {commit!r} is not 40 hex digits: the difference "
                "between the official and cross-check commits cannot be checked"
            )
    changed = git_changed_paths(root, str(official), str(cross))
    for path in changed:
        if ".." in PurePosixPath(path).parts:
            raise ToolError(
                f"git lists the path {path!r} with a '..' component: refused"
            )
    outside = [
        p
        for p in changed
        if not (p.startswith(RECORDS_PREFIX) or p == LEDGER_PATH)
    ]
    if outside:
        raise ToolError(
            "the cross-check commit differs from the official commit and "
            f"changes {len(outside)} path(s) outside {RECORDS_PREFIX} and the "
            f"ledger, first {outside[0]!r}: refused"
        )
    return (
        f"git diff --name-only lists {len(changed)} path(s), all under "
        f"{RECORDS_PREFIX} or the ledger"
    )


def classify(provenance: dict, what: str) -> str:
    """Return "development" or "confirmatory"; refuse any other mix.

    A development run has ``seed_kind`` development, a ``seed_id`` that starts
    with ``DEV-`` and a label without CONFIRMATORY. A confirmatory run has
    ``seed_kind`` confirmatory and a ``seed_id`` that starts with ``CONF-``.
    A file that is neither (for example seed id CONF-1 with kind development)
    is refused, never treated as development.
    """
    kind = provenance.get("seed_kind")
    seed = str(provenance.get("seed_id"))
    label = str(provenance.get("label"))
    if (
        kind == "development"
        and seed.startswith("DEV-")
        and "CONFIRMATORY" not in label.upper()
    ):
        return "development"
    if kind == "confirmatory" and seed.startswith("CONF-"):
        return "confirmatory"
    raise ToolError(
        f"{what}: seed_kind {kind!r}, seed_id {seed!r} and label {label!r} "
        "do not describe a development or a confirmatory run: refused"
    )


def read_sources(
    paths: dict[str, Path], constants: dict, base: Path | None = None
) -> dict:
    """Load every source file; refuse a results file that lacks a system.

    ``paths`` holds ``official``, ``official_md``, ``crosscheck``, ``td`` and
    optionally ``dev``. The official results must list exactly the three
    systems of v3 in ``config.core_systems``. ``base`` is the directory that
    a relative REF or NEW path of the ``compare_runs`` text is read against
    in a development build (default: the working directory); a confirmatory
    build needs absolute ``official``, ``crosscheck`` and ``td`` paths and
    absolute REF and NEW paths, and binds by realpath only (N3).
    """
    sources = {
        "official": read_json(paths["official"]),
        "crosscheck": read_json(paths["crosscheck"]),
        "official_md": parse_results_md(paths["official_md"]),
        "td": parse_td(paths["td"]),
        "const": constants,
    }
    if "dev" in paths:
        sources["dev"] = read_json(paths["dev"])
    sources["official_words"] = sources["official"]
    listed = sources["official"].get("config", {}).get("core_systems")
    if listed != constants["systems"]:
        raise ToolError(
            f"config.core_systems is {listed!r}, not the three systems of v3 "
            f"{constants['systems']!r}: refused"
        )
    if sources["official_md"]["banner"] is None:
        raise ToolError("RESULTS.md has no label line")
    if paths["official"].resolve() == paths["crosscheck"].resolve():
        raise ToolError("the cross-check file is the official file: refused")
    strict = (
        classify(
            sources["official"].get("provenance") or {}, "official results"
        )
        == "confirmatory"
    )
    if strict:
        for name in ("official", "crosscheck", "td"):
            if not paths[name].is_absolute():
                raise ToolError(
                    f"a confirmatory build needs an absolute path for "
                    f"{name}, got {str(paths[name])!r}: refused"
                )
        paths = {name: path.resolve() for name, path in paths.items()}
    sources["td_binding"] = bind_td(
        sources, paths, Path.cwd() if base is None else base, strict
    )
    return sources


def same_run(
    text_path: str, results: Path, base: Path, strict: bool = False
) -> str | None:
    """Say how a path printed by ``compare_runs`` matches a results file.

    Returns "realpath" if both name the same directory. In a development
    build (``strict`` False) a relative printed path is read against
    ``base`` and, if only the last two path components agree (the text may
    have been made with another prefix), the answer is "trailing two path
    components (development mode only)". In a confirmatory build (``strict``)
    a relative printed path is refused and only realpath binds. Otherwise
    None.
    """
    printed = Path(text_path)
    if not printed.is_absolute():
        if strict:
            raise ToolError(
                f"the compare_runs text prints the relative path "
                f"{text_path!r}: a confirmatory build needs absolute REF and "
                "NEW paths (rerun compare_runs with absolute paths)"
            )
        printed = base / printed
    elif strict and Path(os.path.realpath(printed)) != printed:
        raise ToolError(
            f"the compare_runs text prints {text_path!r}, which is not its "
            "own realpath (a link or a '..' component): a confirmatory build "
            "needs REF and NEW paths that are real paths"
        )
    printed = printed.parent if printed.name == "results.json" else printed
    ours = results.parent
    if printed.resolve() == ours.resolve():
        return "realpath"
    if not strict and printed.parts[-2:] == ours.parts[-2:]:
        return "trailing two path components (development mode only)"
    return None


def bind_td(
    sources: dict, paths: dict[str, Path], base: Path, strict: bool = False
) -> str:
    """Tie the ``compare_runs`` text to the two results files (R17, N3).

    The text's REF line must be the official run and its NEW line the
    cross-check, by realpath or, in a development build only, failing that,
    by the last two path components (the tool cannot know the prefix the
    text was made under). A relative path is read against ``base``.
    Every differing verdict-type leaf that the text lists must exist in both
    results files with the printed values. No z value or verdict is
    recomputed, so a text with the right paths and leaves but altered z
    values is not detected; the owner compares the text with a rerun of
    ``compare_runs``. Returns the sentence for the document.
    """
    total = sources["td"]["total"]
    ref = same_run(total["ref"], paths["official"], base, strict)
    new = same_run(total["new"], paths["crosscheck"], base, strict)
    if ref is None or new is None:
        swapped = (
            same_run(total["ref"], paths["crosscheck"], base, strict)
            is not None
        )
        raise ToolError(
            "the compare_runs text was made in the other order (REF is the "
            "cross-check): rerun it with the official run first"
            if swapped
            else "the REF and NEW lines of the compare_runs text do not name "
            f"the official and cross-check runs ({total['ref']!r}, "
            f"{total['new']!r}): refused"
        )
    for path, was, now in sources["td"]["leaves"]:
        keys = "/".join(
            re.sub(r"^\[(\d+)\]$", r"\1", k) for k in path.split("/")
        )
        for name, text in (("official", was), ("crosscheck", now)):
            try:
                value = repr(walk(sources[name], keys))
            except Missing:
                raise ToolError(
                    f"compare_runs lists {path}, which is not in the {name} "
                    "results: refused"
                ) from None
            if value != text:
                raise ToolError(
                    f"compare_runs lists {path} as {text} for the {name} "
                    f"run, the results store {value}: refused"
                )
    return (
        f"REF is the official run and NEW the cross-check (by {ref} and {new})"
    )


def manifest_text(name: str, sha: str, given: str | None, needed: bool) -> str:
    """Compare a file hash with the hash given for the manifest row."""
    if given is None:
        if needed:
            raise ToolError(
                f"a confirmatory run needs the manifest hash of {name}"
            )
        return "none given"
    if not SHA_HEX.match(given.lower()):
        raise ToolError(f"manifest hash of {name} is not 64 hex digits")
    if given.lower() != sha:
        raise ToolError(f"{name} SHA-256 {sha} differs from the manifest hash")
    return "given"


def require_frozen_run(prov: dict, what: str, backend: str) -> None:
    """Refuse a confirmatory run that is not the frozen kind (A9, R16).

    Both runs must be complete and clean. The official run must be a CPU run
    with ``LPC_THREADS`` 8 (v3 section 9 items 2 and 3); the cross-check must
    be a GPU run. Applied to confirmatory builds only: development runs, such
    as the DEV-2 pair, are built whatever they recorded. The cross-check's
    commit may differ from the official one; it is printed, not refused.
    """
    wanted = {"complete": True, "dirty": False}
    if what == "official":
        wanted["LPC_THREADS"] = "8"
    for key, required in wanted.items():
        found = (
            (prov.get("env") or {}).get(key)
            if key == "LPC_THREADS"
            else prov.get(key)
        )
        if found != required:
            raise ToolError(
                f"{what} run: {key} is {found!r}, required {required!r}: "
                "refused"
            )
    found = (prov.get("device") or {}).get("backend")
    if found != backend:
        raise ToolError(
            f"{what} run: device backend is {found!r}, required {backend!r}: "
            "refused"
        )


def make_meta(
    sources: dict,
    shas: dict,
    manifest: dict,
    release_ref: str | None,
    stem: str,
    root: Path,
) -> dict:
    """Apply the release guard and return the builder's ``meta`` values.

    The checks are listed in the module docstring, with what they cannot
    verify. Raises ``ToolError`` when a check fails.
    """
    official = sources["official"].get("provenance") or {}
    cross = sources["crosscheck"].get("provenance") or {}
    mode = classify(official, "official results")
    if classify(cross, "cross-check results") != mode:
        raise ToolError("official and cross-check runs are of different kinds")
    if official.get("seed_id") != cross.get("seed_id"):
        raise ToolError("official and cross-check runs have different seeds")
    if "dev" in sources:
        dev = sources["dev"].get("provenance") or {}
        if classify(dev, "--development file") != "development":
            raise ToolError("--development must be a development run: refused")
    if sources["official_md"]["banner"] != banner_rule(official):
        raise ToolError("RESULTS.md label line differs from provenance.label")
    confirmatory = mode == "confirmatory"
    if confirmatory:
        require_frozen_run(official, "official", "cpu")
        require_frozen_run(cross, "cross-check", "gpu")
    if shas["official"] == shas["crosscheck"]:
        raise ToolError("official and cross-check results are the same file")
    if confirmatory and not (release_ref and RELEASE_REF.match(release_ref)):
        raise ToolError(
            "a confirmatory build needs --release-ref ledger-seq-<n> "
            "(the release record of WU-0015.4): refused"
        )
    checks = [
        manifest_text(n, shas[n], manifest.get(n), confirmatory)
        for n in ("official", "official_md", "crosscheck")
    ]
    if confirmatory:
        frozen = git_freeze_commit(root)
        if official.get("commit") != frozen:
            raise ToolError(
                f"official commit {official.get('commit')} is not "
                f"freeze-1 {frozen}"
            )
        freeze = "equals freeze-1"
    else:
        freeze = "not applicable (development run)"
    if official.get("commit") == cross.get("commit"):
        later = "not needed (the same commit)"
    elif confirmatory:
        later = check_later_commit(
            root, official.get("commit"), cross.get("commit")
        )
    else:
        later = "not checked (development run)"
    return {
        "mode": mode,
        "freeze_check": freeze,
        "official_sha": shas["official"],
        "official_md_sha": shas["official_md"],
        "crosscheck_sha": shas["crosscheck"],
        "manifest_check": (
            "hashes of the three files given at build and equal to them "
            "(the tool cannot read the manifest)"
            if all(c == "given" for c in checks)
            else "none given (development)"
        ),
        "release_ref": (
            f"{release_ref} (format checked only; not verified against the "
            "ledger by this tool)"
            if confirmatory
            else "none (development dry run)"
        ),
        "td_binding": sources["td_binding"],
        "cross_commit_same": (
            "yes" if official.get("commit") == cross.get("commit") else "no"
        ),
        "cross_commit_check": later,
        "cross_commit_differs": (
            "0" if official.get("commit") == cross.get("commit") else "1"
        ),
        "trace_name": f"{stem}.trace.csv",
        "mode_notice": (
            "**DEVELOPMENT DRY RUN (WU-0020.3).** Every number below comes "
            "from a development seed. It rehearses the build and is not a "
            "result of the study."
            if not confirmatory
            else "Source: the official CPU run of the sealed confirmatory "
            "seed. Verdicts are read from the file and not recomputed."
        ),
    }


def build_document(
    sources: dict, constants: dict, directory: Path, stem: str
) -> tuple[str, Builder]:
    """Fill the template; write the figures under ``directory``."""
    builder = Builder(sources, constants, directory, stem)
    text = builder.finalize(builder.expand(TEMPLATE_PATH.read_text()))
    return text, builder


def write_trace(rows: list[Row], path: Path) -> None:
    """Write the trace file: one row per quoted value."""
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(TRACE_COLUMNS)
        for k, r in enumerate(rows):
            writer.writerow(
                [
                    k,
                    r.tag,
                    r.source,
                    r.path,
                    r.spec,
                    r.raw,
                    r.rendered,
                    r.line,
                    r.col,
                ]
            )


TRACE_COLUMNS = [
    "id",
    "tag",
    "source",
    "path",
    "spec",
    "raw",
    "rendered",
    "line",
    "col",
]


def paths_of(args: argparse.Namespace) -> dict[str, Path]:
    """Return the source files named on the command line."""
    official = Path(args.official)
    official = official / "results.json" if official.is_dir() else official
    cross = Path(args.crosscheck)
    cross = cross / "results.json" if cross.is_dir() else cross
    paths = {
        "official": official,
        "official_md": official.parent / "RESULTS.md",
        "crosscheck": cross,
        "td": Path(args.td),
    }
    if args.development:
        dev = Path(args.development)
        paths["dev"] = dev / "results.json" if dev.is_dir() else dev
    for name, path in paths.items():
        if not path.is_file():
            raise ToolError(f"{name} file not found: {path}")
    return paths


def render(args: argparse.Namespace) -> int:
    """Write the document, trace, sources file and figures; then check."""
    constants = read_json(CONSTANTS_PATH)
    paths = paths_of(args)
    sources = read_sources(paths, constants)
    shas = {n: sha256_of(p) for n, p in paths.items()}
    manifest = {
        "official": args.manifest_official,
        "official_md": args.manifest_official_md,
        "crosscheck": args.manifest_crosscheck,
    }
    sources["meta"] = make_meta(
        sources, shas, manifest, args.release_ref, args.stem, HERE.parent
    )
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    text, builder = build_document(sources, constants, out, args.stem)
    (out / f"{args.stem}.md").write_text(text)
    write_trace(builder.rows, out / f"{args.stem}.trace.csv")
    record = {
        "files": {n: str(p.resolve()) for n, p in paths.items()},
        "sha256": shas,
        "manifest": manifest,
        "release_ref": args.release_ref,
        "cwd": str(Path.cwd()),
        "meta": builder.meta,
    }
    (out / f"{args.stem}.sources.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    print(
        f"rendered {args.stem}: {len(builder.rows)} traced values, "
        f"{len(set(builder.missing))} leaves not recorded, "
        f"{len(set(builder.nulls))} null leaves"
    )
    return run_check(out, args.stem, {})


# --- check ------------------------------------------------------------
def split_sections(text: str) -> list[tuple[str, list[str]]]:
    """Split a document at its ``## `` headings (the first part has none)."""
    sections: list[tuple[str, list[str]]] = [("", [])]
    for line in text.split("\n"):
        if line.startswith("## "):
            sections.append((line, []))
        else:
            sections[-1][1].append(line)
    return sections


def merge_free_slots(
    expected: str, actual: str
) -> tuple[str, list[tuple[int, str, bool]], list[str]]:
    """Put a fresh render's text into the two free slots of the document.

    The body of section 11 may differ, and section 9 may carry extra lines
    after the rendered ones. Returns ``(text, free, problems)``: the document
    with those slots replaced by the fresh text (so that line positions match
    the trace again); the lines taken out of the slots as ``(document line,
    text, dated)`` (``dated`` is True for section 9), to be checked by
    ``check_free_slots``; and a problem if the headings differ.
    """
    want, have = split_sections(expected), split_sections(actual)
    if [h for h, _ in want] != [h for h, _ in have]:
        return actual, [], ["the section headings differ from a fresh render"]
    lines: list[str] = []
    free: list[tuple[int, str, bool]] = []
    start = 0  # index of the first line of the section in the document
    for (heading, fresh), (_, found) in zip(want, have):
        body = found
        first = start + (1 if heading else 0)
        if heading.startswith("## 11."):
            free += [(first + k + 1, x, False) for k, x in enumerate(found)]
            body = fresh
        elif heading.startswith("## 9."):
            fresh_trim, found_trim = list(fresh), list(found)
            while fresh_trim and not fresh_trim[-1]:
                fresh_trim.pop()
            while found_trim and not found_trim[-1]:
                found_trim.pop()
            if found_trim[: len(fresh_trim)] == fresh_trim:
                k0 = len(fresh_trim)
                free += [
                    (first + k0 + k + 1, x, True)
                    for k, x in enumerate(found_trim[k0:])
                ]
                body = fresh
        lines += ([heading] if heading else []) + body
        start += (1 if heading else 0) + len(found)
    return "\n".join(lines), free, []


def hidden_text(text: str) -> list[str]:
    """Name what in a free-slot line can hide or disguise a word (V2 to V5).

    A line is refused if it holds an invisible format character (Unicode
    category Cf), an HTML entity ``&...;``, an HTML tag or comment ``<...``,
    or after NFKC a letter outside the Latin script (so a Cyrillic look-alike
    is refused and "Rössler" is not).
    """
    norm = unicodedata.normalize("NFKC", text)
    out = []
    if any(unicodedata.category(ch) == "Cf" for ch in text):
        out.append("an invisible format character")
    if HTML_ENTITY.search(norm):
        out.append("an HTML entity (&...;)")
    if HTML_TAG.search(norm):
        out.append("an HTML tag or comment")
    if any(
        ch.isalpha() and "LATIN" not in unicodedata.name(ch, "") for ch in norm
    ):
        out.append("a letter outside the Latin script")
    return out


def line_core(text: str) -> str:
    """Return a line with NFKC applied and leading ``>`` and list marks cut.

    Used by the heading tests, so a heading inside a quote or a list item is
    found as a heading.
    """
    norm = unicodedata.normalize("NFKC", text)
    return norm[LEADING_MARKS.match(norm).end() :]


def check_free_slots(
    free: list[tuple[int, str, bool]],
    constants: dict,
    floor: date | None,
    today: date | None = None,
) -> list[str]:
    """Check the text of the two free slots (R18, R19, V2 to V5).

    Free text may say what the student thinks, and nothing that looks like
    a number, a status or a section. The threat model is accidental
    misstatement, not a hostile author: the owner and the WU-0020.8 reviewer
    read every claim in the free slots. In section 11 and in the dated lines
    of section 9 (``- YYYY-MM-DD: text``, a real calendar date not before the
    official run ended and not after ``today``, default ``date.today()``):

    * Every line is first checked by ``hidden_text``: no invisible format
      character, no HTML entity or tag, no letter outside the Latin script.
    * Then it is normalized: NFKC (fullwidth and mathematical letters become
      plain ones) and ``*``, ``_`` and the backtick are cut before words,
      stems and brackets are matched, so ``__CONFIRMATORY__``, ``PRO*MOTED*``
      and ``un_promoted`` are found.
    * No numeric character of any kind (the Unicode categories Nd, Nl and No,
      and any character with a numeric value), except the 14 hypothesis
      names such as H2a.
    * No heading line, after cutting leading ``>`` and list marks: a ``#``
      line, or a line followed by a line of only ``=`` or ``-``.
    * No bracketed capitalized token ``[...]`` with any inner text.
    * None of the words banned in PRE-REGISTERED sections or listed as
      ``free_slot_refused`` (case-insensitive, whole words), and no word that
      begins with a stem of ``free_slot_stems`` (proved, confirmed,
      significantly, gates, provisionally, promotion and others).

    Problems name the document line.
    """
    ids = {
        i["key"]
        for i in constants["identifiers"]
        if re.match(r"H\d[a-e]$", i["key"])
    }
    words = constants["banned_phrases"] + constants["free_slot_refused"]
    today = date.today() if today is None else today
    by_number = {number: text for number, text, _ in free}
    problems = []
    for number, text, dated in free:
        if not text.strip():
            continue
        where = f"line {number}"
        for reason in hidden_text(text):
            problems.append(f"{where}: {reason} in a free slot")
        if dated:
            found = DATED_LINE.match(text)
            try:
                when = date.fromisoformat(found.group(1)) if found else None
            except ValueError:
                when = None
            if found is None or when is None:
                problems.append(
                    f"{where}: extra section 9 line is not '- <real date>: "
                    f"text': {text!r}"
                )
                continue
            if floor is not None and when < floor:
                problems.append(f"{where}: date {when} is before the run ended")
            if when > today:
                problems.append(
                    f"{where}: date {when} is after today ({today})"
                )
            text = text[found.end() :]
        core = line_core(text)
        if core.startswith("#"):
            problems.append(f"{where}: heading inside a free slot")
        under = by_number.get(number + 1)
        if (
            not dated
            and under is not None
            and core.strip()
            and not SETEXT_UNDERLINE.fullmatch(core)
            and SETEXT_UNDERLINE.fullmatch(line_core(under))
        ):
            problems.append(
                f"{where}: setext heading (underlined by line {number + 1}) "
                "inside a free slot"
            )
        bare = MARKDOWN_NOISE.sub("", text)
        clean = HYPOTHESIS_ID.sub(
            lambda m: " " if m.group(0) in ids else m.group(0), bare
        )
        for ch in clean:
            if unicodedata.category(ch) in ("Nd", "Nl", "No") or (
                unicodedata.numeric(ch, None) is not None
            ):
                problems.append(
                    f"{where}: numeric character {ch!r} in a free slot "
                    "(write numbers as words)"
                )
                break
        plain = MARKDOWN_NOISE.sub("", unicodedata.normalize("NFKC", text))
        if BRACKET_CAPITAL.search(plain):
            problems.append(
                f"{where}: a bracketed capitalized token [..] inside a free slot"
            )
        for word in words:
            if re.search(rf"\b{re.escape(word)}\b", plain, re.I):
                problems.append(
                    f"{where}: refused word {word!r} in a free slot"
                )
        for stem in constants["free_slot_stems"]:
            if re.search(rf"\b{re.escape(stem)}", plain, re.I):
                problems.append(
                    f"{where}: word beginning with refused stem {stem!r} in a "
                    "free slot"
                )
    return problems


def run_end_date(official: dict) -> date | None:
    """Return the date the official run ended (None if not stored)."""
    try:
        return date.fromisoformat(official["provenance"]["end_utc"][:10])
    except (KeyError, TypeError, ValueError):
        return None


def diff_sections(expected: str, actual: str) -> list[str]:
    """Name the first section in which two documents differ."""
    problems = []
    want, have = split_sections(expected), split_sections(actual)
    if [h for h, _ in want] != [h for h, _ in have]:
        return ["the section headings differ from a fresh render"]
    for (heading, a), (_, b) in zip(want, have):
        if a != b:
            first = next(
                (k for k, (x, y) in enumerate(zip(a, b)) if x != y),
                min(len(a), len(b)),
            )
            problems.append(
                f"{heading or 'the preamble'!r} differs from a fresh render "
                f"at its line {first + 1}"
            )
    return problems


def check_rows(rows: list[dict], lines: list[str], sources: dict) -> list[str]:
    """Re-resolve every trace row and compare it with the document."""
    problems = []
    constants = sources["const"]
    for r in rows:
        try:
            where = f"row {r['id']} ({r['source']}:{r['path']})"
            if r["source"] not in sources:
                problems.append(f"{where}: unknown source")
                continue
            if r["source"] not in ALLOWED.get(r["tag"], set()):
                problems.append(
                    f"{where}: source not allowed in a "
                    f"{r['tag'] or 'plain'} section"
                )
            try:
                value = walk(sources[r["source"]], r["path"])
                raw, text = repr(value), fmt(value, r["spec"])
            except Missing:
                raw, text = MISSING, NOT_RECORDED
            if raw != r["raw"] or text != r["rendered"]:
                problems.append(
                    f"{where}: leaf gives {text!r}, trace says {r['rendered']!r}"
                )
            line, col = int(r["line"]), int(r["col"])
            found = (
                lines[line - 1][col : col + len(r["rendered"])]
                if 1 <= line <= len(lines)
                else ""
            )
            if found != r["rendered"]:
                problems.append(
                    f"{where}: document has {found!r} at line {line}"
                )
            if r["source"] == "const" and not const_citation(
                constants, r["path"]
            ):
                problems.append(f"{where}: constant without a v3 citation")
        except (KeyError, ValueError, TypeError, ToolError, Missing) as exc:
            problems.append(f"row {r.get('id')}: malformed ({exc!r})")
    return problems


def untraced_numbers(lines: list[str], rows: list[dict]) -> list[str]:
    """Return lines that hold a digit the trace and the identifiers do not.

    Traced spans are blanked, then the identifier shapes of the study
    (``IDENTIFIER``), then any remaining digit is a number nobody traced.
    Dated lines appended to section 9 lose their date first. Number words
    ("forty-two") cannot be detected.
    """
    masked = list(lines)
    for r in rows:
        try:
            k, col, n = int(r["line"]) - 1, int(r["col"]), len(r["rendered"])
        except (KeyError, ValueError, TypeError):
            continue  # a malformed row is reported by ``check_rows``
        if 0 <= k < len(masked):
            masked[k] = masked[k][:col] + " " * n + masked[k][col + n :]
    bad = []
    for k, line in enumerate(masked):
        clean = IDENTIFIER.sub(" ", line)
        hit = re.search(r"\d", clean)
        if hit:
            bad.append(
                f"line {k + 1}: untraced number near {clean[hit.start() : hit.start() + 12]!r}"
            )
    return bad


def check_text(lines: list[str], sources: dict, rows: list[dict]) -> list[str]:
    """Banner, language, required phrases, completeness and PROVISIONAL."""
    problems = []
    constants = sources["const"]
    official = sources["official"]
    expected = banner_rule(official["provenance"])
    if not lines or lines[0] != expected:
        problems.append(f"line 1 is not the provenance banner {expected!r}")
    if len(lines) < 2 or lines[1] != PRELIMINARY_LINE:
        problems.append("line 2 is not the PRELIMINARY line")
    tags = section_tags("\n".join(lines))
    for k, (line, tag) in enumerate(zip(lines, tags)):
        if tag == "PRE-REGISTERED":
            for phrase in constants["banned_phrases"]:
                if phrase.lower() in line.lower():
                    problems.append(f"line {k + 1}: banned phrase {phrase!r}")
    text = "\n".join(lines)
    for phrase in constants["required_phrases"]:
        if phrase not in text:
            problems.append(f"missing required phrase {phrase!r}")
    start = text.find("## 10.")
    limits = text[start : text.find("## 11.")] if start >= 0 else ""
    for word in constants["limitation_keywords"]:
        if word.lower() not in limits.lower():
            problems.append(f"limitations lack {word!r}")
    paths = {(r["source"], r["path"]) for r in rows}
    systems = constants["systems"]
    for item in constants["identifiers"]:
        for s in systems:
            if (
                "official",
                f"verdicts/{item['key']}/by_system/{s}",
            ) not in paths:
                problems.append(
                    f"{item['key']} of {s} missing from the verdict table"
                )
        if ("official", f"verdicts/{item['key']}/verdict") not in paths:
            problems.append(f"identifier {item['key']} missing")
    for s in systems:
        block = (official.get("systems") or {}).get(s) or {}
        for part in constants["primary_parts"]:
            if ("official", f"systems/{s}/{part['estimate']}") not in paths:
                problems.append(f"primary part {s} {part['name']} missing")
        for gate in constants["gate_rows"]:
            for _, leaf, _ in gate["stats"]:
                if ("official", f"systems/{s}/{leaf}") not in paths:
                    problems.append(f"{gate['check']} of {s} missing")
        gate_pass = block.get("validation", {}).get("gate", {}).get("gate_pass")
        if gate_pass is not True:
            rows_s = [x for x in lines if x.startswith(f"| {s}")]
            if not rows_s or any("PROVISIONAL" not in x for x in rows_s):
                problems.append(
                    f"{s} failed the gate but a row lacks PROVISIONAL"
                )
            for r in rows:
                if r["source"] == "official" and r["path"].endswith(
                    f"/by_system/{s}"
                ):
                    line, col = int(r["line"]), int(r["col"]) + len(
                        r["rendered"]
                    )
                    if not lines[line - 1][col:].startswith(" PROVISIONAL"):
                        problems.append(
                            f"verdict cell {r['path']} lacks PROVISIONAL"
                        )
    for name in walk(official, "handling/totals"):
        if ("official", f"handling/totals/{name}") not in paths:
            problems.append(f"handling counter {name} missing")
    if ("official", "handling/failed_variants") not in paths:
        problems.append("failed_variants missing")
    return problems


def run_check(directory: Path, stem: str, override: dict) -> int:
    """Check the document in ``directory``; print problems; return 0 or 1.

    Order: hash every source, apply the release guard again, render a fresh
    copy (with figures) in a temporary directory, and compare it with the
    document, the trace and the three PNG files; then run the independent
    checks on the document text.
    """
    record = read_json(directory / f"{stem}.sources.json")
    constants = read_json(CONSTANTS_PATH)
    paths = {
        name: Path(override.get(name) or path)
        for name, path in record["files"].items()
    }
    for name, path in paths.items():
        if not path.is_file() or sha256_of(path) != record["sha256"][name]:
            raise ToolError(f"{name} changed since the build: {path}")
    if not isinstance(record.get("cwd"), str):
        raise ToolError("sources.json has no cwd: rebuild the document")
    sources = read_sources(paths, constants, Path(record["cwd"]))
    sources["meta"] = make_meta(
        sources,
        record["sha256"],
        record["manifest"],
        record["release_ref"],
        stem,
        HERE.parent,
    )
    actual = (directory / f"{stem}.md").read_text()
    with (directory / f"{stem}.trace.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        fresh, builder = build_document(sources, constants, Path(tmp), stem)
        merged, free, extra = merge_free_slots(fresh, actual)
        problems += extra + diff_sections(fresh, merged)
        problems += check_free_slots(
            free, constants, run_end_date(sources["official"])
        )
        lines = merged.split("\n")
        if builder.meta != record["meta"]:
            problems.append("meta values differ from a fresh render")
        expected_rows = [
            [
                str(k),
                r.tag,
                r.source,
                r.path,
                r.spec,
                r.raw,
                r.rendered,
                str(r.line),
                str(r.col),
            ]
            for k, r in enumerate(builder.rows)
        ]
        got_rows = [[r.get(c, "") for c in TRACE_COLUMNS] for r in rows]
        if expected_rows != got_rows:
            problems.append("the trace file differs from a fresh render")
        for name in ("F1_primary", "F2_secondary", "F3_crosscheck"):
            old = directory / f"{stem}.figures" / f"{name}.png"
            new = Path(tmp) / f"{stem}.figures" / f"{name}.png"
            if not old.is_file() or old.read_bytes() != new.read_bytes():
                problems.append(f"figure {name} differs from a fresh render")
    problems += check_rows(rows, lines, sources)
    problems += untraced_numbers(lines, rows)
    problems += check_text(lines, sources, rows)
    for p in problems[:50]:
        print(f"CHECK FAIL: {p}")
    print(
        f"check {'FAILED' if problems else 'passed'}: {len(rows)} traced "
        f"values, {len(problems)} problems"
    )
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    ren = sub.add_parser("render", help="write the document, trace and figures")
    ren.add_argument(
        "--official", required=True, help="run dir or results.json"
    )
    ren.add_argument(
        "--crosscheck", required=True, help="run dir or results.json"
    )
    ren.add_argument("--td", required=True, help="compare_runs text file")
    ren.add_argument("--development", help="development run dir (appendix A)")
    ren.add_argument("--out", required=True)
    ren.add_argument("--stem", default="preliminary_findings")
    ren.add_argument("--release-ref", help="ledger-seq-<n>; confirmatory only")
    ren.add_argument(
        "--manifest-official", help="manifest SHA-256, results.json"
    )
    ren.add_argument(
        "--manifest-official-md", help="manifest SHA-256, RESULTS.md"
    )
    ren.add_argument(
        "--manifest-crosscheck", help="manifest SHA-256, cross-check"
    )
    chk = sub.add_parser("check", help="verify a rendered document")
    chk.add_argument("directory")
    chk.add_argument("--stem", default="preliminary_findings")
    for name in ("official", "official_md", "crosscheck", "td", "dev"):
        chk.add_argument(
            f"--{name}", help=f"use this {name} file (hash is checked)"
        )
    args = parser.parse_args(argv)
    try:
        if args.command == "render":
            return render(args)
        override = {
            n: getattr(args, n)
            for n in ("official", "official_md", "crosscheck", "td", "dev")
            if getattr(args, n)
        }
        return run_check(Path(args.directory), args.stem, override)
    except ToolError as exc:
        print(f"findings_build: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
