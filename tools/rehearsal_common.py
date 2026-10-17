"""DEVELOPMENT: code shared by ``tools/rehearsal_report.py`` and ``tools/rehearsal_diagnostics.py``.

WU-0003.10 (plan amendment 7, G4). **Needs owner review before freeze** (statistics code: the two
tools feed the sample-size and block-length decisions; this module only holds what they had in
common). Development seeds only; no random number is drawn here; nothing in ``lpcstudy/`` is imported.

What moved, with no change of behaviour (the two tools' reports are byte-identical to the golden
files in ``tests/unit/fixtures/golden_rehearsal/``): the three exception classes, the ``Report``
collector and ``attempt``, the dump reader ``Dump``, the results-tree access ``dig`` and ``fmt``, the
seed-id and results-file helpers (``is_dev_id``, ``run_seed_id``, ``make_label``, ``find_results``,
``load_results``), the JSON serializer ``json_ready`` and the exit-code and schema constants.

What did NOT move, and why (recorded in the unit Log, WU-0003.10): ``block_variance`` and the
influence-series builders (``influence_diff`` and ``influence_ratio`` of the report tool, ``psi_mean``
and ``psi_ratio`` of the diagnostics) differ in substance between the two tools (the report tool's
``block_variance`` refuses a non-finite entry and has a default block length; the diagnostics' does not
check and has no default; the influence builders differ in the finiteness and domain checks). They stay
in their tools until the owner or the planner rules which behaviour governs.

Exit codes of both tools: 0 everything computed and reproduced, 1 a MISMATCH (takes precedence),
2 anything not computable.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

EXIT_MISMATCH = 1
EXIT_INCOMPLETE = 2
SCHEMAS = ("lpcstudy.states/1", "lpcstudy.states/2")
PRIMARY_LEVEL = 1.0 - 0.05 / 3.0


# --------------------------------------------------------------------------------------------
# errors and the report
# --------------------------------------------------------------------------------------------
class NotComputable(Exception):
    """A quantity cannot be formed from the data given (never replaced by a number)."""


class Missing(NotComputable):
    """A leaf or array that the computation needs is not in the file."""


class Refused(NotComputable):
    """The run is refused (a seed id that is not a development seed, or disagreeing ids)."""


@dataclass
class Report:
    """Lines, the "not computable" and mismatch lists, and the numbers (for ``--json``)."""

    lines: list[str] = field(default_factory=list)
    incomplete: list[str] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def say(self, text: str = "") -> None:
        """Add a line."""
        self.lines.append(text)

    def nc(self, where: str, why: str) -> None:
        """Record and print a quantity that cannot be computed (counts toward exit 2)."""
        line = f"not computable: {where}: {why}"
        self.incomplete.append(line)
        self.lines.append("  " + line)

    def internal(self, where: str, exc: Exception) -> None:
        """Record and print an unexpected exception (never lost, never read as a MISMATCH)."""
        import traceback
        frame = traceback.extract_tb(exc.__traceback__)[-1]
        line = (f"INTERNAL ERROR: {where}: {type(exc).__name__}: {exc} "
                f"(at {Path(frame.filename).name}:{frame.lineno} in {frame.name})")
        self.incomplete.append(line)
        self.lines.append("  " + line)

    def defect(self, text: str, label: str = "MISMATCH") -> None:
        """Record and print a MISMATCH (or, with ``label``, another defect such as the DEFECT of C4)."""
        self.defects.append(text)
        self.lines.append(f"  {label}: " + text)

    def exit_code(self) -> int:
        """1 on a mismatch, else 2 on anything not computable, else 0."""
        return EXIT_MISMATCH if self.defects else (EXIT_INCOMPLETE if self.incomplete else 0)


def attempt(rep: Report, where: str, fn: Callable, *args, **kwargs):
    """Call ``fn``; a ``NotComputable`` is recorded under ``where`` and ``None`` is returned.

    Any other exception is recorded as an INTERNAL ERROR (exit 2) and also returns ``None``, so
    the rest of the report is still computed; a ``Refused`` is never caught.
    """
    try:
        return fn(*args, **kwargs)
    except Refused:
        raise
    except NotComputable as exc:
        rep.nc(where, str(exc))
        return None
    except Exception as exc:  # noqa: BLE001  (unexpected: reported, exit 2)
        rep.internal(where, exc)
        return None


class Dump:
    """One system's ``states/<system>.npz`` (or a dict of the same keys, for tests)."""

    def __init__(self, arrays, source: str) -> None:
        self._arrays = arrays
        self.source = source

    @classmethod
    def load(cls, path: Path) -> Dump:
        """Open an archive (never with pickles)."""
        return cls(np.load(path, allow_pickle=False), str(path))

    def close(self) -> None:
        """Close the archive (a dict has nothing to close)."""
        if hasattr(self._arrays, "close"):
            self._arrays.close()

    def has(self, key: str) -> bool:
        """Whether the key is present."""
        return key in self._arrays

    def __getitem__(self, key: str) -> np.ndarray:
        if key not in self._arrays:
            raise Missing(f"array {key!r} is not in {self.source}")
        return np.asarray(self._arrays[key])

    def scalar(self, key: str):
        """A 0-d array as a Python scalar."""
        return self[key].item()


def dig(tree: dict, *path: str):
    """A leaf of the results tree; ``Missing`` if any key is absent or the leaf is None."""
    node = tree
    for key in path:
        if not isinstance(node, dict) or key not in node:
            raise Missing(f"results leaf {'/'.join(path)} is absent")
        node = node[key]
    if node is None:
        raise Missing(f"results leaf {'/'.join(path)} is null")
    return node


def fmt(x: float | None, digits: int = 4) -> str:
    """A number for a report line; None prints as ``n/a``."""
    if x is None:
        return "n/a"
    return f"{x:.{digits}g}"


# --------------------------------------------------------------------------------------------
# seeds and files
# --------------------------------------------------------------------------------------------
def is_dev_id(seed_id: object) -> bool:
    """Whether a recorded seed id is a development id ``DEV-n``."""
    return isinstance(seed_id, str) and seed_id.startswith("DEV-") and seed_id[4:].isdigit()


def run_seed_id(results: dict) -> str:
    """The run's seed id: ``config.seed_id`` and ``provenance.seed_id`` must both be present, agree
    and be ``DEV-n``, and a recorded ``provenance.seed_kind`` must be ``development``.

    Raises
    ------
    Refused
        Otherwise.
    """
    cfg, prov = results.get("config"), results.get("provenance")
    if not isinstance(cfg, dict) or not isinstance(prov, dict):
        raise Refused("refused: results.json has no config block or no provenance block")
    ids = {"config.seed_id": cfg.get("seed_id"), "provenance.seed_id": prov.get("seed_id")}
    for where, value in ids.items():
        if not is_dev_id(value):
            raise Refused(f"refused: {where} is {value!r}, not a development seed id DEV-n")
    if ids["config.seed_id"] != ids["provenance.seed_id"]:
        raise Refused(f"refused: the recorded seed ids disagree: {ids}")
    if prov.get("seed_kind") != "development":
        raise Refused(f"refused: provenance.seed_kind is {prov.get('seed_kind')!r}, not "
                      "'development'")
    return str(ids["config.seed_id"])


def make_label(seed_id: str | None) -> str:
    """The DEVELOPMENT label with the seed id the run recorded."""
    return f"DEVELOPMENT ({seed_id}): conditional on one realization; not a hypothesis test"


def find_results(path: Path) -> Path:
    """The ``results.json`` of a run (a file, or the directory that holds it)."""
    target = path / "results.json" if path.is_dir() else path
    if not target.is_file():
        raise NotComputable(f"no results.json at {path}")
    return target


def load_results(path: Path) -> tuple[Path, dict, str]:
    """Read a run: the file, the parsed tree and its (validated) development seed id."""
    target = find_results(path)
    try:
        results = json.loads(target.read_text())
    except (OSError, ValueError) as exc:
        raise NotComputable(f"{target} is unreadable: {exc}") from exc
    if not isinstance(results, dict):
        raise NotComputable(f"{target} does not hold a JSON object")
    return target, results, run_seed_id(results)


def json_ready(obj):
    """``obj`` with numpy values and non-finite floats made JSON-safe (NaN and inf become null)."""
    if isinstance(obj, dict):
        return {str(k): json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_ready(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return json_ready(obj.tolist())
    if isinstance(obj, (np.floating, float)):
        return None if not math.isfinite(float(obj)) else float(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj
