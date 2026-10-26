"""DEVELOPMENT: code shared by ``tools/rehearsal_report.py`` and
``tools/rehearsal_diagnostics.py``.

The two rehearsal tools read the saved results of a development run and print
reports that help the owner choose the sample sizes and block lengths of the
full study. Both need the same small building blocks: a way to open a run and
check that it uses a development seed (never the sealed one), a way to read the
per-state arrays that a run dumps, a collector for report lines, and a rule that
a number that cannot be computed is said so and is never replaced by a guess.
This module holds those blocks once so that the two tools cannot drift apart
(WU-0003.10, plan amendment 7, G4). It draws no random numbers and imports
nothing from ``lpcstudy``. Needs owner review before freeze (statistics code).

What lives here: the three exception classes, the ``Report`` collector and
``attempt``, the dump reader ``Dump``, the results-tree access ``dig`` and
``fmt``, the seed and file helpers (``is_dev_id``, ``run_seed_id``,
``make_label``, ``find_results``, ``load_results``), the JSON converter
``json_ready``, and the exit-code and schema constants. The move changed no
behavior: the reports of both tools are byte-identical to the golden files in
``tests/unit/fixtures/golden_rehearsal/``.

What does not live here: ``block_variance`` (a variance estimate for resampling
in blocks) and the builders of the influence series. They differ in substance
between the two tools. For example, the report tool's ``block_variance`` refuses
a non-finite entry and has a default block length, while the diagnostics tool's
does neither. They stay in their own tools until the owner or the planner rules
which behavior governs (unit Log, WU-0003.10).

Exit codes of both tools: 0 when everything was computed and reproduced, 1 for a
MISMATCH (this wins over 2), 2 when anything was not computable.
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
SCHEMAS = ("lpcstudy.states/1", "lpcstudy.states/2", "lpcstudy.states/3")
PRIMARY_LEVEL = 1.0 - 0.05 / 3.0


# ------------------------------------------------------------------------------
# errors and the report
# ------------------------------------------------------------------------------
class NotComputable(Exception):
    """A quantity cannot be formed from the data given (it is never replaced by
    a number).
    """


class Missing(NotComputable):
    """A value or array that the computation needs is not in the file."""


class Refused(NotComputable):
    """The run is refused: its seed id is not a development id, or the ids
    disagree.
    """


@dataclass
class Report:
    """Collects the report lines, the problems found, and the numbers behind the
    report.

    Attributes
    ----------
    lines : list of str
        The text of the report, in order.
    incomplete : list of str
        One entry per quantity that could not be computed (counts toward exit
        2).
    defects : list of str
        One entry per mismatch or other defect (counts toward exit 1).
    data : dict
        The numbers, for the ``--json`` output.
    """

    lines: list[str] = field(default_factory=list)
    incomplete: list[str] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def say(self, text: str = "") -> None:
        """Add a line to the report."""
        self.lines.append(text)

    def nc(self, where: str, why: str) -> None:
        """Record and print a quantity that cannot be computed (counts toward
        exit 2).
        """
        line = f"not computable: {where}: {why}"
        self.incomplete.append(line)
        self.lines.append("  " + line)

    def internal(self, where: str, exc: Exception) -> None:
        """Record and print an unexpected exception.

        It is counted toward exit 2, never lost, and never mistaken for a
        MISMATCH.
        """
        import traceback

        frame = traceback.extract_tb(exc.__traceback__)[-1]
        line = (
            f"INTERNAL ERROR: {where}: {type(exc).__name__}: {exc} "
            f"(at {Path(frame.filename).name}:{frame.lineno} in {frame.name})"
        )
        self.incomplete.append(line)
        self.lines.append("  " + line)

    def defect(self, text: str, label: str = "MISMATCH") -> None:
        """Record and print a mismatch, or with ``label`` another kind of
        defect.
        """
        self.defects.append(text)
        self.lines.append(f"  {label}: " + text)

    def exit_code(self) -> int:
        """Return 1 on a mismatch, else 2 if anything was not computable, else
        0.
        """
        return (
            EXIT_MISMATCH
            if self.defects
            else (EXIT_INCOMPLETE if self.incomplete else 0)
        )


def attempt(rep: Report, where: str, fn: Callable, *args, **kwargs):
    """Call ``fn``; if it fails, record why and return ``None``.

    A ``NotComputable`` is recorded under ``where`` as "not computable". Any
    other exception is recorded as an INTERNAL ERROR (exit 2) and also returns
    ``None``, so the rest of the report is still computed. A ``Refused`` is
    never caught: a refused run must stop.

    Parameters
    ----------
    rep : Report
        Where problems are recorded.
    where : str
        A short name of the step, printed with the problem.
    fn : callable
        The function to call, with ``*args`` and ``**kwargs``.
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
    """One system's ``states/<system>.npz`` archive (or a dict with the same
    keys).

    A run can dump per-state arrays, such as the errors of each forecaster at
    each test state. This class reads them by key and turns a missing key into a
    clear ``Missing`` error. The dict form lets tests build small dumps by hand.
    """

    def __init__(self, arrays, source: str) -> None:
        self._arrays = arrays
        self.source = source

    @classmethod
    def load(cls, path: Path) -> Dump:
        """Open an archive from disk (never allowing pickled Python objects)."""
        return cls(np.load(path, allow_pickle=False), str(path))

    def close(self) -> None:
        """Close the archive (a plain dict has nothing to close)."""
        if hasattr(self._arrays, "close"):
            self._arrays.close()

    def has(self, key: str) -> bool:
        """Return whether the key is present."""
        return key in self._arrays

    def __getitem__(self, key: str) -> np.ndarray:
        if key not in self._arrays:
            raise Missing(f"array {key!r} is not in {self.source}")
        return np.asarray(self._arrays[key])

    def scalar(self, key: str):
        """Return a 0-dimensional array as a plain Python number or string."""
        return self[key].item()


def dig(tree: dict, *path: str):
    """Return a leaf of the results tree, or raise ``Missing``.

    ``Missing`` is raised if any key on the path is absent, a step is not a
    dictionary, or the leaf is ``None`` (a number that was not computed).
    """
    node = tree
    for key in path:
        if not isinstance(node, dict) or key not in node:
            raise Missing(f"results leaf {'/'.join(path)} is absent")
        node = node[key]
    if node is None:
        raise Missing(f"results leaf {'/'.join(path)} is null")
    return node


def fmt(x: float | None, digits: int = 4) -> str:
    """Format a number for a report line with ``digits`` significant digits.

    ``None`` prints as ``n/a``.
    """
    if x is None:
        return "n/a"
    return f"{x:.{digits}g}"


# ------------------------------------------------------------------------------
# seeds and files
# ------------------------------------------------------------------------------
def is_dev_id(seed_id: object) -> bool:
    """Return whether a recorded seed id is a development id of the form
    ``DEV-n``.
    """
    return (
        isinstance(seed_id, str)
        and seed_id.startswith("DEV-")
        and seed_id[4:].isdigit()
    )


def run_seed_id(results: dict) -> str:
    """Return the seed id of a run, or refuse the run.

    The run is accepted only if ``config.seed_id`` and ``provenance.seed_id``
    are both present, agree with each other and look like ``DEV-n``, and a
    recorded ``provenance.seed_kind`` is ``development``. This is how the tools
    make sure they never read a run made with the sealed confirmatory seed.

    Raises
    ------
    Refused
        In every other case.
    """
    cfg, prov = results.get("config"), results.get("provenance")
    if not isinstance(cfg, dict) or not isinstance(prov, dict):
        raise Refused(
            "refused: results.json has no config block or no provenance block"
        )
    ids = {
        "config.seed_id": cfg.get("seed_id"),
        "provenance.seed_id": prov.get("seed_id"),
    }
    for where, value in ids.items():
        if not is_dev_id(value):
            raise Refused(
                f"refused: {where} is {value!r}, "
                "not a development seed id DEV-n"
            )
    if ids["config.seed_id"] != ids["provenance.seed_id"]:
        raise Refused(f"refused: the recorded seed ids disagree: {ids}")
    if prov.get("seed_kind") != "development":
        raise Refused(
            f"refused: provenance.seed_kind is {prov.get('seed_kind')!r}, not "
            "'development'"
        )
    return str(ids["config.seed_id"])


def make_label(seed_id: str | None) -> str:
    """Return the DEVELOPMENT label line, with the seed id the run recorded."""
    return (
        f"DEVELOPMENT ({seed_id}): conditional on one realization; "
        "not a hypothesis test"
    )


def find_results(path: Path) -> Path:
    """Return the ``results.json`` of a run, given the file or the directory."""
    target = path / "results.json" if path.is_dir() else path
    if not target.is_file():
        raise NotComputable(f"no results.json at {path}")
    return target


def load_results(path: Path) -> tuple[Path, dict, str]:
    """Read a run and return the file, the tree and its checked seed id."""
    target = find_results(path)
    try:
        results = json.loads(target.read_text())
    except (OSError, ValueError) as exc:
        raise NotComputable(f"{target} is unreadable: {exc}") from exc
    if not isinstance(results, dict):
        raise NotComputable(f"{target} does not hold a JSON object")
    return target, results, run_seed_id(results)


def json_ready(obj):
    """Return ``obj`` with numpy values and non-finite floats made JSON-safe.

    NaN and infinity become ``None`` (JSON null), numpy arrays become lists, and
    numpy numbers become Python numbers.
    """
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
