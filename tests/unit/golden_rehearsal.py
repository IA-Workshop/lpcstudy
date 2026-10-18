"""Golden-output cases and runner for the two rehearsal tools (WU-0003.10).

What this module does for the study
-----------------------------------
Before the real run, the study rehearses its analysis on pilot results from
the development seed. Two command-line tools do the rehearsing:
``tools/rehearsal_report.py`` projects the pilot results onto the
pre-registered criteria, and ``tools/rehearsal_diagnostics.py`` checks that
the numbers behind those criteria are consistent. Both tools print text, and
a silent change in that text could change what the study team reads. A
*golden file* is a saved copy of the exact output of a tool on a fixed input.
If the tool's output ever differs from the golden file by even one byte, a
test fails and tells us. (The plan reference is plan amendment 7, item G4,
step h1.)

How the pieces connect
----------------------
* ``produce()`` runs both tools on a fixed list of cases and returns a
  dictionary: file name -> output text.
* The golden files in ``tests/unit/fixtures/golden_rehearsal/`` were written
  by ``produce()`` from the tools as they stood BEFORE
  ``tools/rehearsal_common.py`` (the shared code both tools now use) existed.
  The commit is named in the README of that folder.
* ``tests/unit/test_tools_rehearsal_common.py`` calls ``produce()`` on the
  code under test and compares the text byte for byte. If the shared-code
  refactoring changed any output, that test fails.
* Because a golden file is only a copy of earlier output, it is a regression
  guard (it detects change), not evidence that the output is correct. The
  correctness tests live in the two tool test files.

The test "worlds" (small made-up result sets) are the ones those two tool
test files build (``write_run``, ``make_dump``, ``build_world``). They are
imported from there rather than copied, so the golden cases cannot drift away
from the worlds those tests use.

Machine-dependent text
----------------------
Three kinds of text differ from machine to machine or from run to run, so
they are replaced by placeholders and the golden files hold on any machine:

* the temporary directory of a run becomes ``<TMP>``;
* the repository root becomes ``<ROOT>``;
* the values on the analysis-stack lines of the diagnostics (python, numpy,
  scipy, CPU, BLAS, SIMD, environment) become ``<values>``. The status of
  each line (``same``, ``different`` or ``unusable``) is kept, because that
  status is part of what the tool reports.

Regenerate (only to record a deliberate change of output, with the reason
written in the unit Log)::

    python tests/unit/golden_rehearsal.py tests/unit/fixtures/golden_rehearsal
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for entry in (str(ROOT), str(HERE)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import test_tools_rehearsal_diagnostics as tdiag  # noqa: E402  (after the path lines)
import test_tools_rehearsal_report as trep  # noqa: E402

GOLDEN = HERE / "fixtures" / "golden_rehearsal"
DIAGNOSTIC_OPTIONS = ["--resamples", "100", "--permutations", "50"]
"""Command-line options that keep the diagnostics tool fast.

The tool resamples the data (bootstrap) and shuffles it (permutations) many
times. These small counts are the ones its own tests use; the random seed is
left at the tool's default, so the output is reproducible.
"""


STACK_LINE = re.compile(
    r"^(  (?:python|packages\.\w+|cpu\.\w+|blas\.\w+|numpy_simd\.\w+|env\.\w+)): "
    r"run .*; here .*: (same|different|unusable)$",
    re.MULTILINE,
)
"""Pattern for one line of the diagnostics' analysis-stack comparison.

Each such line says what the pilot run used, what this machine uses, and
whether the two are ``same``, ``different`` or ``unusable``. The values
depend on the machine, so the golden files keep only the status.
"""


def _normalise_text(text: str, tmp: Path) -> str:
    """Replace machine-dependent parts of a tool's text by placeholders.

    The temporary directory becomes ``<TMP>``, the repository root becomes
    ``<ROOT>``, and the values on the stack lines become ``<values>`` (their
    ``same``/``different``/``unusable`` status is kept).
    """
    text = text.replace(str(tmp), "<TMP>").replace(str(ROOT), "<ROOT>")
    return STACK_LINE.sub(r"\1: <values>: \2", text)


def _normalise_json(text: str, tmp: Path) -> str:
    """Normalize a tool's JSON output the same way as ``_normalise_text``.

    In addition, the "run" and "own" values in ``stack.rows`` (the two machine
    dependent columns) become ``<value>``. The JSON must also survive a
    load-and-dump round trip unchanged; if not, the tool's formatting changed
    and the assertion says so.
    """
    text = text.replace(str(tmp), "<TMP>").replace(str(ROOT), "<ROOT>")
    tree = json.loads(text)
    assert (
        json.dumps(tree, indent=1) == text
    ), "the JSON of a tool does not round-trip"
    if isinstance(tree.get("stack"), dict):
        for row in tree["stack"]["rows"]:
            row[1] = row[2] = "<value>"
    return json.dumps(tree, indent=1)


def _call(
    main: Callable[[list[str]], int],
    argv: list[str],
    tmp: Path,
    name: str,
    out_files: dict[str, str],
) -> None:
    """Run one tool call and store what it printed and wrote.

    ``main`` is called with ``argv`` plus a ``--json`` output path. Its exit
    code, standard output and standard error go into ``out_files[name.txt]``,
    and the JSON file (if the tool wrote one) into ``out_files[name.json]``,
    both normalized.
    """
    json_path = tmp / f"{name}.json"
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main([*argv, "--json", str(json_path)])
    text = f"exit code: {code}\n--- stdout ---\n{out.getvalue()}--- stderr ---\n{err.getvalue()}"
    out_files[f"{name}.txt"] = _normalise_text(text, tmp)
    if json_path.exists():
        out_files[f"{name}.json"] = _normalise_json(json_path.read_text(), tmp)


def produce() -> dict[str, str]:
    """Run every golden case of both tools.

    Returns
    -------
    dict[str, str]
        File name -> normalized text. The report tool's cases come first,
        then the diagnostics tool's. The cases cover exit codes 0, 1 and 2
        (success, a mismatch found, an input refused or incomplete), so each way the tools can end is
        guarded.
    """
    files: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="golden_rehearsal_") as raw:
        tmp = Path(raw)
        # ---- tools/rehearsal_report.py
        for fixture in ("p0_pilot", "p1_pilot"):
            _call(
                trep.rr.main,
                [str(trep.FIXTURES / f"{fixture}.json")],
                tmp,
                f"report_{fixture}",
                files,
            )
        worlds = {
            "report_world": {},
            "report_world_best_a0": {"best": "A0"},
            "report_world_h3c_mismatch": {"scale_h3c": 1.0 + 1e-6},
            "report_world_refused_dump": {"dump_seed": "DEV-9"},
        }
        for name, kwargs in worlds.items():
            run = trep.write_run(tmp / name / "run", **kwargs)
            _call(trep.rr.main, [str(run)], tmp, name, files)
        run = tmp / "report_world" / "run" / "results.json"
        observed = trep.observed_file(
            tmp / "observed", {"H1b PLP slope": 1.2, "H2c A4-A2": 2.0}, run
        )
        _call(
            trep.rr.main,
            [str(run.parent), "--observed", str(observed)],
            tmp,
            "report_world_observed",
            files,
        )
        # ---- tools/rehearsal_diagnostics.py
        for fixture in ("p0_pilot", "p1_pilot"):
            _call(
                tdiag.rd.main,
                [str(trep.FIXTURES / f"{fixture}.json"), *DIAGNOSTIC_OPTIONS],
                tmp,
                f"diagnostics_{fixture}",
                files,
            )
        data, res, _ = tdiag.build_world(tdiag.rng_for("world"))
        run = tdiag.write_run(tmp / "diag_world", data, res)
        _call(
            tdiag.rd.main,
            [str(run), *DIAGNOSTIC_OPTIONS],
            tmp,
            "diagnostics_world",
            files,
        )
        data, res, _ = tdiag.build_world(tdiag.rng_for("world"))
        res["systems"]["lorenz63"]["H3c"]["A5_over_A4_mse"] *= 1.000001
        del data["core/Lambda_bar"]
        run = tdiag.write_run(tmp / "diag_mismatch", data, res)
        _call(
            tdiag.rd.main,
            [str(run), *DIAGNOSTIC_OPTIONS],
            tmp,
            "diagnostics_world_mismatch",
            files,
        )
        data, res, _ = tdiag.build_world(tdiag.rng_for("world"))
        del data["core/E_C_A"]
        del data["core/w_star_B"]
        run = tdiag.write_run(tmp / "diag_missing", data, res)
        _call(
            tdiag.rd.main,
            [str(run), *DIAGNOSTIC_OPTIONS],
            tmp,
            "diagnostics_world_missing",
            files,
        )
        data, res, _ = tdiag.build_world(tdiag.rng_for("world"))
        res["provenance"]["packages"]["scipy"] = "0.0.0"
        cell = res["systems"]["lorenz63"]["H1a"]["by_noise"]["0.01"]
        cell["fitted_inverse_dim"] += 2e-5 * tdiag.h1a_scale(res)
        run = tdiag.write_run(tmp / "diag_stack", data, res)
        _call(
            tdiag.rd.main,
            [str(run), *DIAGNOSTIC_OPTIONS],
            tmp,
            "diagnostics_world_other_stack",
            files,
        )
        data, res, _ = tdiag.build_world(tdiag.rng_for("world"))
        (tmp / "diag_nodump").mkdir()
        (tmp / "diag_nodump" / "results.json").write_text(json.dumps(res))
        _call(
            tdiag.rd.main,
            [str(tmp / "diag_nodump")],
            tmp,
            "diagnostics_world_no_dump",
            files,
        )
    return files


def main(argv: list[str]) -> int:
    """Write the golden files into the folder named by ``argv[0]``.

    Use it only to record a deliberate change of a tool's output (see the
    module docstring). Returns the process exit code, 0.
    """
    folder = Path(argv[0])
    folder.mkdir(parents=True, exist_ok=True)
    produced = produce()
    for name, text in sorted(produced.items()):
        (folder / name).write_text(text)
        print(f"{name}: {len(text)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
