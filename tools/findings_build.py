#!/usr/bin/env python3
"""Build and check the preliminary findings document (WU-0020).

The study asks whether four local predictability conditions decide how to
blend an analog forecaster (CP) with a physics-based forecaster (PLP). When
the sealed confirmatory run finishes, the owner and the student need one
short, honest document that says what came out. This tool writes that
document from the stored results and then proves that every number in it
came from a stored file.

Two commands:

* ``render`` reads the official ``results.json`` (with the ``RESULTS.md`` next
  to it), the cross-check ``results.json`` and the ``compare_runs`` text. It
  fills the template ``tools/findings/preliminary.template.md`` and writes
  the document, a trace file (one row per quoted number, with its source and
  leaf path), a ``sources.json`` (paths and SHA-256 hashes) and three
  figures (F1 primary forest plot, F2 secondary forest plot, F3 cross-check).
* ``check`` re-reads the sources and fails if any quoted number differs
  from its leaf, if a number appears that the trace does not explain, if a
  section quotes a source its tag forbids, or if the banner, the language
  rules or the completeness rules fail.

The tool only reads and formats. It computes no statistic and no verdict: a
verdict word in the document is the string stored in the results file, and no
interval is compared with a band. Figures draw the stored estimates and
interval endpoints as they are. Constants of the v3 design (bands, levels,
bars) come from ``tools/findings/design_constants.json``, each with its v3
section. Nothing in ``lpcstudy/`` is imported or changed.

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
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMPLATE_PATH = HERE / "findings" / "preliminary.template.md"
CONSTANTS_PATH = HERE / "findings" / "design_constants.json"
PRELIMINARY_LINE = (
    "PRELIMINARY: internal to the owner and the student until promotion "
    "(QA.11, LPC.PC.13)."
)
MISSING = "<missing>"
NOT_RECORDED = "not recorded"
PLACEHOLDER = re.compile(r"\{\{(\w+)(?::([^}|]*))?(?:\|([^}]*))?\}\}")
MARK = re.compile("\x00(\\d+)\x01(.*?)\x02", re.S)
NUMERAL = re.compile(r"(?<![\w.\-])-?\d+(?:\.\d+)?(?:e[-+]?\d+)?")
STRUCTURE = re.compile(r"§\s*\d+(?:\.\d+)?|^#{1,6} \d+\.|\bitem \d+|`[^`\s]*`")
HEADING = re.compile(r"^(#{2,3}) ")
TAG = re.compile(r"\[([A-Z][A-Z-]+)(?::[^\]]*)?\]\s*$")
SOURCES = (
    "official",
    "official_md",
    "crosscheck",
    "td",
    "dev",
    "const",
    "meta",
)
# Which sources each section tag may quote (A6). Untagged sections may quote
# the official run, the cross-check file and the constants (provenance).
ALLOWED = {
    "PRE-REGISTERED": {"official", "official_md", "const"},
    "DIAGNOSTIC": {"official", "const"},
    "CROSS-CHECK": {"crosscheck", "td", "const"},
    "DEVELOPMENT": {"dev", "const"},
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
        return "not computed"
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


def run_files(target: Path) -> tuple[Path, Path | None]:
    """Return ``results.json`` and the ``RESULTS.md`` beside it (or None)."""
    results = target / "results.json" if target.is_dir() else target
    markdown = results.parent / "RESULTS.md"
    return results, markdown if markdown.exists() else None


def split_cells(line: str) -> list[str]:
    """Split a Markdown table row on pipes that are not escaped."""
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def parse_results_md(path: Path | None) -> dict:
    """Read the banner, interval labels and clip cells of ``RESULTS.md``.

    These three are copied verbatim into the document, so the tool never
    rebuilds them: ``banner`` is the label line of ``report.header_lines``,
    ``label[id]`` is the line of the interval-label list, ``clip[id]`` is the
    last cell of the verdict-table row.
    """
    out: dict = {"banner": None, "label": {}, "clip": {}}
    if path is None:
        return out
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
    document copies it exactly (A10).
    """
    out: dict = {"parts": {}, "total": {"differing": "0"}}
    for line in path.read_text().splitlines():
        row = TD_ROW.match(line)
        if row:
            names = ("d", "z_sym", "z_away", "hw", "status")
            system, part = row.group(1), row.group(2)
            out["parts"].setdefault(system, {})[part] = dict(
                zip(names, row.groups()[2:])
            )
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
    return out


def const_citation(tree: dict, path: str) -> str | None:
    """Return the ``v3`` citation of the deepest entry on a constant path."""
    node, found = tree, None
    for part in path.split("/"):
        node = walk(node, part)
        if isinstance(node, dict) and "v3" in node:
            found = node["v3"]
    return found


# --- the document builder ---------------------------------------------
class Builder:
    """Fill the template and keep the trace of every quoted value.

    A quoted value is written as a marker (``\\x00id\\x01text\\x02``) while the
    text is assembled. ``finalize`` removes the markers and records each
    value's position, so the trace says exactly where every number sits.
    """

    def __init__(
        self, sources: dict, constants: dict, directory: Path, stem: str
    ):
        self.sources = sources
        self.constants = constants
        self.directory = directory
        self.stem = stem
        self.rows: list[Row] = []
        self.missing: list[str] = []
        official = sources["official"]
        self.systems = [
            s
            for s in walk(official, "config/core_systems")
            if s in official["systems"]
        ]
        self.provisional = {
            s: self.gate_state(s) is not True for s in self.systems
        }

    def gate_state(self, system: str) -> object:
        """Return the stored ``gate_pass`` of a system (None if absent)."""
        try:
            return walk(
                self.sources["official"],
                f"systems/{system}/validation/gate/gate_pass",
            )
        except Missing:
            return None

    def ref(self, source: str, path: str, spec: str = "") -> str:
        """Quote one leaf and record it; a missing leaf is "not recorded"."""
        try:
            value = walk(self.sources[source], path)
            raw, text = repr(value), fmt(value, spec)
        except Missing:
            raw, text = MISSING, NOT_RECORDED
            self.missing.append(f"{source}:{path}")
        self.rows.append(Row(source, path, spec, raw, text))
        return f"\x00{len(self.rows) - 1}\x01{text}\x02"

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
            ("Manifest check", "meta", "official_manifest", ""),
            ("Release reference", "meta", "release_ref", ""),
            ("Cross-check seed id", "crosscheck", "provenance/seed_id", ""),
            (
                "Cross-check backend",
                "crosscheck",
                "provenance/device/backend",
                "",
            ),
            ("Cross-check SHA-256", "meta", "crosscheck_sha", ""),
            ("Cross-check manifest", "meta", "crosscheck_manifest", ""),
        ]
        return ["| Item | Value |", "|---|---|"] + [
            f"| {name} | {self.ref(src, path, spec)} |"
            for name, src, path, spec in rows
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
            cells = [
                self.ref("official", f"verdicts/{key}/by_system/{s}", "verdict")
                + self.mark(s)
                for s in self.systems
            ]
            out.append(
                f"| {key} | {item['role']} | {' | '.join(cells)} | "
                f"{self.ref('official', f'verdicts/{key}/verdict', 'verdict')}"
                f" | {self.ref('official_md', f'clip/{key}')} |"
            )
        return out

    def parts_rows(
        self, parts_key: str, default_level: str, notes: bool
    ) -> list[str]:
        """Rows of a parts table: estimate, interval, level, band, verdict."""
        head = ["System", "Part", "Estimate", "Interval", "Level", "Band"]
        head += ["Verdict"] + (["Notes"] if notes else [])
        out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for s in self.systems:
            for i, part in enumerate(self.constants[parts_key]):
                level = part["level"]
                if level and self.has_leaf(s, level):
                    level_cell = self.official(s, level, ".4f")
                else:
                    level_cell = self.const(default_level)
                spec = "" if part["verdict"].endswith("/reading") else "verdict"
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
        return out + ["", f"Failed robustness variants: {failed}."]

    def table_crosscheck(self) -> list[str]:
        """The TD table of the cross-check and its totals."""
        out = [
            "| System | Part | d | z_sym (information) | z_away (governs) | "
            "hw1/hw0 | Status |",
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
        gates = ", ".join(
            f"{s} "
            + self.ref(
                "crosscheck", f"systems/{s}/validation/gate/gate_pass", "yn"
            )
            for s in self.systems
        )
        out += [
            "",
            f"Parts computed {total('computed')} of {total('expected')}; "
            f"sum of z squared (away) {total('sum_away')}; "
            f"largest z (away) {total('max_away')}; "
            f"failing parts {total('failing')} (bound {self.const('td_bound')}).",
            "",
            f"Verdict-type leaves that differ between the two runs: "
            f"{total('differing')}. compare_runs result: {total('result')}.",
            "",
            f"GPU validation gate passed: {gates}.",
        ]
        return out

    def table_labels(self) -> list[str]:
        """Interval labels copied from RESULTS.md, one per identifier."""
        return [
            "- " + self.ref("official_md", f"label/{item['key']}")
            for item in self.constants["identifiers"]
        ]

    # --- text blocks --------------------------------------------------
    def wording_primary(self) -> str:
        """One sentence template per primary row, picked by the stored word."""
        wording = self.constants["wording"]
        lines = []
        for key in ("H2a", "H2b", "H3c", "H2c"):
            path = f"verdicts/{key}/verdict"
            try:
                word = walk(self.sources["official"], path)
            except Missing:
                word = None
            text = wording.get(word, NOT_RECORDED) if word else NOT_RECORDED
            if word == "not supported" and f"reading:{key}" in wording:
                text += " " + wording[f"reading:{key}"]
            lines.append(
                f"- **{key}**: {self.ref('official', path, 'verdict')}. {text}"
            )
        return "\n".join(lines)

    def wording_gpu(self) -> str:
        """Agree or disagree sentence for the cross-check (no new verdict)."""
        total = self.sources["td"]["total"]
        gates = [
            walk(
                self.sources["crosscheck"],
                f"systems/{s}/validation/gate/gate_pass",
            )
            for s in self.systems
            if self.has_cross_gate(s)
        ]
        bad = (
            total.get("failing", "x") != "0"
            or total.get("differing", "x") != "0"
            or not total.get("result", "").startswith("PASS")
            or any(g is not True for g in gates)
            or len(gates) != len(self.systems)
        )
        return self.constants["wording"]["gpu_disagree" if bad else "gpu_agree"]

    def has_cross_gate(self, system: str) -> bool:
        """Return True if the cross-check file stores this system's gate."""
        try:
            walk(
                self.sources["crosscheck"],
                f"systems/{system}/validation/gate/gate_pass",
            )
            return True
        except Missing:
            return False

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
        file = {"F1": "F1_primary", "F2": "F2_secondary", "F3": "F3_crosscheck"}
        path = figures / f"{file[name]}.png"
        if name == "F3":
            fig = draw_crosscheck(self.sources["td"], self.constants, label)
        else:
            key = "primary_parts" if name == "F1" else "secondary_parts"
            panels = panel_data(
                self.sources["official"],
                self.constants[key]
                + (self.constants["qn_parts"] if name == "F2" else []),
                self.systems,
            )
            marks = {s: self.provisional[s] for s in self.systems}
            cols = 3 if name == "F1" else 4
            fig = draw_panels(panels, cols, label, marks)
        save_figure(fig, path)
        alt = f"{name}: {file[name]}"
        return (
            f"![{alt}]({self.stem}.figures/{path.name})\n\n"
            f"*{self.const('caption_' + name)}*"
        )

    def missing_note(self) -> str:
        """Count and list the leaves that were not found (PRIME.4)."""
        unique = sorted(set(self.missing))
        count = self.sources["meta"]["missing_count"] = str(len(unique))
        text = [
            f'Leaves not found in the sources, written "{NOT_RECORDED}": '
            f"{self.ref('meta', 'missing_count')}."
        ]
        text += [f"- `{path}`" for path in unique]
        return "\n".join(text) if count else text[0]

    def expand(self, template: str) -> str:
        """Replace every placeholder of the template, in order."""
        simple = {
            "gate_box": self.gate_box,
            "dev_appendix": self.dev_appendix,
        }

        def replace(match: re.Match) -> str:
            kind, arg, spec = match.group(1), match.group(2), match.group(3)
            if kind in SOURCES:
                if kind == "const":
                    return self.const(arg)
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
                return self.sources["meta"]["mode_notice"]
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
    for line in text.splitlines():
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
OKABE_READING = "#CC79A7"
BAND_COLOR = "#56B4E9"
MARKERS = {"pass": "o", "fail": "X", "inconclusive": "D"}


def panel_data(official: dict, parts: list[dict], systems: list[str]) -> list:
    """Collect the stored estimate, interval and verdict of each panel.

    Returns one dict per part with ``name``, ``band`` and ``points`` (one
    entry per system: ``(est, lo, hi, label)`` or None if not recorded).
    The numbers are the leaves as stored: nothing is recomputed.
    """
    panels = []
    for part in parts:
        points = []
        for s in systems:
            base = f"systems/{s}/"
            try:
                est = float(walk(official, base + part["estimate"]))
                lo, hi = (
                    float(v) for v in walk(official, base + part["interval"])
                )
                label = str(walk(official, base + part["verdict"]))
                points.append((est, lo, hi, label))
            except (Missing, TypeError, ValueError):
                points.append(None)
        panels.append(
            {
                "name": part["name"],
                "experiment": part["experiment"],
                "band": part["band"],
                "points": points,
            }
        )
    return panels


def draw_panels(
    panels: list, columns: int, label: str, provisional: dict
) -> plt.Figure:
    """Draw one small panel per part: markers, interval bars and band.

    Marker shape and text carry the verdict, so color is never the only cue.
    A system that failed the validation gate is named PROVISIONAL on its
    row of every panel.
    """
    rows = -(-len(panels) // columns)
    fig, axes = plt.subplots(
        rows, columns, figsize=(4.2 * columns, 2.1 * rows + 0.9), squeeze=False
    )
    names = list(provisional)
    for ax in axes.flat[len(panels) :]:
        ax.axis("off")
    for ax, panel in zip(axes.flat, panels):
        ends = [v for p in panel["points"] if p for v in p[1:3]]
        ends += [b for b in panel["band"] if b is not None]
        low, high = (min(ends), max(ends)) if ends else (0.0, 1.0)
        pad = 0.08 * (high - low or 1.0)
        low, high = low - pad, high + pad
        band = [low if b is None else b for b in panel["band"][:1]] + [
            high if b is None else b for b in panel["band"][1:]
        ]
        ax.axvspan(band[0], band[1], color=BAND_COLOR, alpha=0.2, lw=0)
        for y, (name, point) in enumerate(zip(names, panel["points"])):
            if point is None:
                ax.text(low, y, " not recorded", va="center", fontsize=7)
                continue
            est, lo, hi, word = point
            color = OKABE.get(word, OKABE_READING)
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
        ax.tick_params(axis="x", labelsize=7)
        ax.set_title(f"{panel['name']} ({panel['experiment']})", fontsize=8)
    fig.suptitle(label, fontsize=9)
    fig.tight_layout()
    return fig


def crosscheck_points(td: dict, constants: dict) -> list[tuple[str, float]]:
    """Return ``(system part, z_away)`` for every parsed TD row."""
    points = []
    for system in td["parts"]:
        for part in constants["primary_parts"]:
            row = td["parts"][system].get(part["name"])
            if row:
                points.append(
                    (f"{system} {part['name']}", float(row["z_away"]))
                )
    return points


def draw_crosscheck(td: dict, constants: dict, label: str) -> plt.Figure:
    """Draw the cross-check z values, in gray, with the bound line."""
    points = crosscheck_points(td, constants)
    fig, ax = plt.subplots(figsize=(6.0, 0.3 * len(points) + 1.4))
    ys = list(range(len(points)))
    ax.plot([z for _, z in points], ys, "o", color="#555555")
    bound = float(constants["constants"]["td_bound"]["text"])
    ax.axvline(bound, color="#555555", ls="--")
    ax.set_yticks(ys)
    ax.set_yticklabels([n for n, _ in points], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("z (away arm)")
    ax.set_title("Cross-check, information only", fontsize=9)
    fig.suptitle(label, fontsize=8)
    fig.tight_layout()
    return fig


def save_figure(fig: plt.Figure, path: Path) -> None:
    """Save a PNG with no timestamp or software tag (byte-identical reruns)."""
    fig.savefig(path, dpi=130, metadata={"Software": None})
    plt.close(fig)


# --- render -----------------------------------------------------------
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


def manifest_text(sha: str, given: str | None, needed: bool, what: str) -> str:
    """Compare a file hash with the manifest row; refuse a mismatch."""
    if given is None:
        if needed:
            raise ToolError(
                f"a confirmatory run needs the {what} manifest hash"
            )
        return "no manifest row given (development)"
    if given.lower() != sha:
        raise ToolError(f"{what} SHA-256 {sha} differs from the manifest row")
    return "equals the manifest row"


def load_sources(args: argparse.Namespace, root: Path) -> tuple[dict, dict]:
    """Load every source named on the command line and build ``meta``."""
    constants = read_json(CONSTANTS_PATH)
    official_json, official_md = run_files(Path(args.official))
    cross_json, _ = run_files(Path(args.crosscheck))
    official, cross = read_json(official_json), read_json(cross_json)
    prov = official.get("provenance") or {}
    kind = prov.get("seed_kind")
    if kind is None:
        raise ToolError("the official results carry no provenance.seed_kind")
    confirmatory = kind == "confirmatory"
    if confirmatory and not args.release_ref:
        raise ToolError(
            "a confirmatory results.json needs --release-ref (the release "
            "record of WU-0015.4): refused"
        )
    if prov.get("seed_id") != (cross.get("provenance") or {}).get("seed_id"):
        raise ToolError("official and cross-check runs have different seeds")
    markdown = parse_results_md(official_md)
    if markdown["banner"] != banner_rule(prov):
        raise ToolError("RESULTS.md banner differs from provenance.label")
    shas = {
        "official": sha256_of(official_json),
        "crosscheck": sha256_of(cross_json),
    }
    if confirmatory:
        frozen = git_freeze_commit(root)
        if prov.get("commit") != frozen:
            raise ToolError(
                f"official commit {prov.get('commit')} is not freeze-1 {frozen}"
            )
        freeze = "equals freeze-1"
    else:
        freeze = "not applicable (development run)"
    meta = {
        "freeze_check": freeze,
        "official_sha": shas["official"],
        "crosscheck_sha": shas["crosscheck"],
        "official_manifest": manifest_text(
            shas["official"], args.manifest_official, confirmatory, "official"
        ),
        "crosscheck_manifest": manifest_text(
            shas["crosscheck"],
            args.manifest_crosscheck,
            confirmatory,
            "cross-check",
        ),
        "release_ref": args.release_ref or "none (development dry run)",
        "trace_name": f"{args.stem}.trace.csv",
        "missing_count": "0",
        "mode_notice": (
            "**DEVELOPMENT DRY RUN (WU-0020.3).** Every number below comes "
            "from a development seed. It rehearses the build and is not a "
            "result of the study."
            if not confirmatory
            else "Source: the official CPU run of the sealed confirmatory "
            "seed. Verdicts are read from the file and not recomputed."
        ),
    }
    sources = {
        "official": official,
        "official_md": markdown,
        "crosscheck": cross,
        "td": parse_td(Path(args.td)),
        "const": constants,
        "meta": meta,
    }
    files = {
        "official": str(official_json.resolve()),
        "crosscheck": str(cross_json.resolve()),
        "td": str(Path(args.td).resolve()),
    }
    if args.development:
        dev_json, _ = run_files(Path(args.development))
        sources["dev"] = read_json(dev_json)
        files["dev"] = str(dev_json.resolve())
    return sources, files


def write_trace(rows: list[Row], path: Path) -> None:
    """Write the trace file: one row per quoted value."""
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
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
        )
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


def render(args: argparse.Namespace) -> int:
    """Write the document, trace, sources file and figures; then check."""
    root = HERE.parent
    sources, files = load_sources(args, root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    constants = sources["const"]
    builder = Builder(sources, constants, out, args.stem)
    text = builder.finalize(builder.expand(TEMPLATE_PATH.read_text()))
    (out / f"{args.stem}.md").write_text(text)
    write_trace(builder.rows, out / f"{args.stem}.trace.csv")
    record = {
        "files": files,
        "sha256": {k: sha256_of(Path(v)) for k, v in files.items()},
        "meta": sources["meta"],
        "mode": (
            "confirmatory"
            if sources["official"]["provenance"]["seed_kind"] == "confirmatory"
            else "development"
        ),
    }
    (out / f"{args.stem}.sources.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    missing = sorted(set(builder.missing))
    print(
        f"rendered {args.stem}: {len(builder.rows)} traced values, "
        f"{len(missing)} leaves not recorded"
    )
    return run_check(out, args.stem, {})


# --- check ------------------------------------------------------------
def rebuild_sources(record: dict, constants: dict, override: dict) -> dict:
    """Reload the sources named in ``sources.json`` (paths may be overridden)."""
    sources: dict = {"const": constants, "meta": record["meta"]}
    paths = {
        name: Path(override.get(name) or path)
        for name, path in record["files"].items()
    }
    for name, path in paths.items():
        if sha256_of(path) != record["sha256"][name]:
            raise ToolError(f"{name} changed since the build: {path}")
        sources[name] = parse_td(path) if name == "td" else read_json(path)
    markdown = paths["official"].parent / "RESULTS.md"
    sources["official_md"] = parse_results_md(
        markdown if markdown.exists() else None
    )
    return sources


def check_rows(rows: list[dict], lines: list[str], sources: dict) -> list[str]:
    """Re-resolve every trace row and compare it with the document."""
    problems = []
    constants = sources["const"]
    for r in rows:
        where = f"row {r['id']} ({r['source']}:{r['path']})"
        if r["source"] not in ALLOWED.get(r["tag"], set()):
            problems.append(
                f"{where}: source not allowed in a {r['tag'] or 'plain'} section"
            )
        try:
            value = walk(sources[r["source"]], r["path"])
            raw, text = repr(value), fmt(value, r["spec"])
        except Missing:
            raw, text = MISSING, NOT_RECORDED
        except ToolError as exc:
            problems.append(f"{where}: {exc}")
            continue
        if raw != r["raw"] or text != r["rendered"]:
            problems.append(
                f"{where}: leaf gives {text!r}, trace says {r['rendered']!r}"
            )
        line, col = int(r["line"]), int(r["col"])
        found = (
            lines[line - 1][col : col + len(r["rendered"])]
            if line <= len(lines)
            else ""
        )
        if found != r["rendered"]:
            problems.append(f"{where}: document has {found!r} at line {line}")
        if r["source"] == "const" and not const_citation(constants, r["path"]):
            problems.append(f"{where}: constant without a v3 citation")
    return problems


def untraced_numbers(lines: list[str], rows: list[dict]) -> list[str]:
    """Return lines that hold a numeral the trace does not explain."""
    masked = list(lines)
    for r in rows:
        k, col, n = int(r["line"]) - 1, int(r["col"]), len(r["rendered"])
        masked[k] = masked[k][:col] + " " * n + masked[k][col + n :]
    bad = []
    for k, line in enumerate(masked):
        clean = STRUCTURE.sub(" ", line)
        hits = NUMERAL.findall(clean)
        if hits:
            bad.append(f"line {k + 1}: untraced number {hits[0]!r}")
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
    for item in constants["identifiers"]:
        if ("official", f"verdicts/{item['key']}/verdict") not in paths:
            problems.append(
                f"identifier {item['key']} missing from the verdict table"
            )
    systems = [
        s
        for s in walk(official, "config/core_systems")
        if s in official["systems"]
    ]
    for s in systems:
        for part in constants["primary_parts"]:
            leaf = f"systems/{s}/{part['estimate']}"
            if ("official", leaf) not in paths:
                problems.append(f"primary part {s} {part['name']} missing")
        for gate in constants["gate_rows"]:
            for _, leaf, _ in gate["stats"]:
                if ("official", f"systems/{s}/{leaf}") not in paths:
                    problems.append(f"{gate['check']} of {s} missing")
        if ("official", f"systems/{s}/validation/gate/gate_pass") not in paths:
            problems.append(f"gate of {s} missing")
        gate = official["systems"][s].get("validation", {}).get("gate", {})
        if gate.get("gate_pass") is not True:
            rows_s = [x for x in lines if x.startswith(f"| {s}")]
            if not rows_s or any("PROVISIONAL" not in x for x in rows_s):
                problems.append(
                    f"{s} failed the gate but a row lacks PROVISIONAL"
                )
    totals = walk(official, "handling/totals")
    for name in totals:
        if ("official", f"handling/totals/{name}") not in paths:
            problems.append(f"handling counter {name} missing")
    if ("official", "handling/failed_variants") not in paths:
        problems.append("failed_variants missing")
    return problems


def run_check(directory: Path, stem: str, override: dict) -> int:
    """Check the document in ``directory``; print problems; return 0 or 1."""
    record = read_json(directory / f"{stem}.sources.json")
    constants = read_json(CONSTANTS_PATH)
    sources = rebuild_sources(record, constants, override)
    lines = (directory / f"{stem}.md").read_text().split("\n")
    with (directory / f"{stem}.trace.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    problems = check_rows(rows, lines, sources)
    problems += untraced_numbers(lines, rows)
    problems += check_text(lines, sources, rows)
    for name in ("F1_primary", "F2_secondary", "F3_crosscheck"):
        if not (directory / f"{stem}.figures" / f"{name}.png").exists():
            problems.append(f"figure {name} missing")
    for p in problems[:50]:
        print(f"CHECK FAIL: {p}")
    print(
        f"check {'FAILED' if problems else 'passed'}: {len(rows)} traced values, "
        f"{len(problems)} problems"
    )
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    ren = sub.add_parser("render", help="write the document, trace and figures")
    ren.add_argument(
        "--official", required=True, help="official run dir or results.json"
    )
    ren.add_argument(
        "--crosscheck",
        required=True,
        help="cross-check run dir or results.json",
    )
    ren.add_argument("--td", required=True, help="compare_runs text file")
    ren.add_argument("--development", help="development run dir (appendix A)")
    ren.add_argument("--out", required=True)
    ren.add_argument("--stem", default="preliminary_findings")
    ren.add_argument(
        "--release-ref",
        help="release record (WU-0015.4); required for a confirmatory run",
    )
    ren.add_argument(
        "--manifest-official",
        help="manifest SHA-256 of the official results.json",
    )
    ren.add_argument(
        "--manifest-crosscheck",
        help="manifest SHA-256 of the cross-check results.json",
    )
    chk = sub.add_parser("check", help="verify a rendered document")
    chk.add_argument("directory")
    chk.add_argument("--stem", default="preliminary_findings")
    for name in ("official", "crosscheck", "td", "development"):
        chk.add_argument(
            f"--{name}",
            help=f"use this {name} file instead of the recorded path",
        )
    args = parser.parse_args(argv)
    try:
        if args.command == "render":
            return render(args)
        override = {
            n: getattr(args, n)
            for n in ("official", "crosscheck", "td", "development")
            if getattr(args, n)
        }
        override = {
            n: str(run_files(Path(v))[0]) if n != "td" else v
            for n, v in override.items()
        }
        return run_check(Path(args.directory), args.stem, override)
    except ToolError as exc:
        print(f"findings_build: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
