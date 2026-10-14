"""Command-line seed handling of ``python -m lpcstudy`` (WU-0001.1, .3).

Everything is exact (exit codes, strings). The study is never run here: only refusals and
seed resolution are exercised, and the confirmatory seed is never used (LPC.PC.7).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lpcstudy.__main__ import build_parser, choose_seed, main
from lpcstudy.seeds import REGISTRY_PATH

PREFIX = "lpcstudy: refused (LPC.PC.7): "


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test sees a confirmatory seed or salt (LPC.PC.7)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)


def resolve(argv: list[str]) -> tuple[str, int]:
    """Parse ``argv`` and resolve the seed against the real development registry."""
    args, extras = build_parser().parse_known_args(argv)
    return choose_seed(args, extras, REGISTRY_PATH)


def test_default_and_explicit_ids_resolve() -> None:
    """No flag gives DEV-0 (20261005); ``--seed-id DEV-1`` gives the registry value.

    Reference: the literal 20261005 and ``json.load`` of the registry. Exact.
    """
    with REGISTRY_PATH.open() as handle:
        expected = next(e["value"] for e in json.load(handle)["seeds"] if e["id"] == "DEV-1")
    assert resolve([]) == ("DEV-0", 20261005)
    assert resolve(["--seed-id", "DEV-0"]) == ("DEV-0", 20261005)
    assert resolve(["--seed-id=DEV-1"]) == ("DEV-1", expected)


def test_abbreviations_are_off() -> None:
    """``allow_abbrev`` is false, so ``--conf`` cannot stand for a longer flag.

    Reference: the plan (parser built with ``allow_abbrev=False``). Exact.
    """
    assert build_parser().allow_abbrev is False


@pytest.mark.parametrize("argv", [
    ["--seed", "5"],
    ["--seed", "20261005"],
    ["--seed=5"],
    ["--seed"],
    ["--seed-id", "5"],
    ["--seed-id=20261005"],
    ["--seed-id", "dev-1"],
    ["--seed-id", "DEV-99"],
    ["--seed-id", "CONF-1"],
    ["--conf"],
    ["--conf=123"],
    ["--seed-i", "DEV-0"],
    ["5"],
    ["--preset", "smoke", "--seed", "5", "--seed-id", "DEV-0"],
])
def test_refusal_is_one_line_exit_64_and_creates_nothing(
        argv: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Each refused request returns 64 with one stderr line naming LPC.PC.7 and writes nothing.

    Reference: the refusal contract of the plan (exit 64; exactly one stderr line
    ``lpcstudy: refused (LPC.PC.7): <reason>``; nothing created before it). The seed
    values in ``argv`` (5, 20261005, 123) must not be echoed. Exact string and integer checks.
    """
    out = tmp_path / "out"
    code = main([*argv, "--out", str(out)])
    captured = capsys.readouterr()
    assert code == 64
    assert captured.out == ""
    lines = captured.err.splitlines()
    assert len(lines) == 1 and lines[0].startswith(PREFIX)
    assert not out.exists() and not list(tmp_path.rglob("results.json"))
    for value in ("20261005", "=5", " 5", "=123"):
        assert value not in lines[0]


@pytest.mark.parametrize("token", ["-424242424242", "--424242424242", "--conf", "--conf=424242",
                                   "--seed-i"])
def test_unrecognized_token_is_never_echoed(token: str, tmp_path: Path,
                                            capsys: pytest.CaptureFixture[str]) -> None:
    """An unrecognized dash token (a seed-like number or an abbreviation) is not echoed.

    Reference: the refusal contract (values never echoed; review R2 probe
    ``-424242424242``). The stderr line must contain no part of the token: neither the token,
    nor its text after the dashes, nor its value after ``=``. Exact substring checks.
    """
    assert main([token, "--out", str(tmp_path / "out")]) == 64
    err = capsys.readouterr().err
    lines = err.splitlines()
    assert len(lines) == 1 and lines[0].startswith(PREFIX)
    name, _, value = token.partition("=")
    for part in (token, name.lstrip("-"), value):
        if part:
            assert part not in lines[0], (part, lines[0])


def test_removed_skip_transfer_option_is_refused(tmp_path: Path,
                                                 capsys: pytest.CaptureFixture[str]) -> None:
    """``--skip-transfer`` no longer exists: exit 64 and one stderr line, nothing created.

    Reference: the refusal contract of ``choose_seed`` (an unrecognized option is refused,
    WU-0002.1). Exact integer and string checks, no tolerance.
    """
    out = tmp_path / "out"
    assert main(["--skip-transfer", "--out", str(out)]) == 64
    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == "" and len(lines) == 1 and lines[0].startswith(PREFIX)
    assert "unrecognized option" in lines[0] and "skip-transfer" not in lines[0]  # never echoed
    assert not out.exists()


def test_refusal_does_not_set_up_logging(tmp_path: Path) -> None:
    """A refusal adds no logging handler (refusals precede logging setup).

    Reference: the plan's order (refuse before ``out_dir.mkdir``, logging and ``Study``).
    """
    import logging
    before = list(logging.getLogger().handlers)
    assert main(["--seed", "5", "--out", str(tmp_path / "o")]) == 64
    assert list(logging.getLogger().handlers) == before


def test_registry_path_is_a_python_parameter_only() -> None:
    """No flag redirects the registry or the ledger (Q8).

    Reference: the parser's option strings. Exact.
    """
    options = {s for action in build_parser()._actions for s in action.option_strings}
    assert not {o for o in options if "ledger" in o or "registry" in o}


# ------------------------------------------------------------ WU-0001.3: the confirmatory flag
# In-process only, with a throwaway ledger in tmp_path and synthetic seeds (LPC.PC.7).

SEED = 123456789012345
SALT = "0f" * 16
FLAG = "--confirmatory"


def ledger_with(path: Path, seed: int) -> Path:
    """A one-entry hash-chained ledger holding the ``CONF-1`` commitment of ``seed``."""
    import hashlib
    digest = hashlib.sha256(f"{seed}:{SALT}".encode()).hexdigest()
    record = {"seq": 1, "prev_sha256": "0" * 64, "utc": "2026-01-01T00:00:00+00:00",
              "type": "commitment", "actor": "test", "role": "test", "authority": "",
              "summary": "synthetic", "files": {},
              "data": {"seed_id": "CONF-1", "sha256": digest}}
    path.write_text(json.dumps(record, sort_keys=True) + "\n")
    return path


def test_confirmatory_flag_returns_the_verified_seed_under_conf_1(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With matching synthetic variables the flag resolves to ``("CONF-1", seed)``.

    Reference: the synthetic seed literal; the ledger is built in the test with hashlib.
    Exact. The study is not run.
    """
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    args, extras = build_parser().parse_known_args([FLAG])
    assert choose_seed(args, extras, REGISTRY_PATH,
                       ledger_with(tmp_path / "l.jsonl", SEED)) == ("CONF-1", SEED)


@pytest.mark.parametrize("argv, set_env", [
    ([FLAG, "--seed-id", "DEV-0"], True),     # mutually exclusive, even with valid variables
    ([FLAG], False),                          # no variables
    ([FLAG, "--seed", "5"], True),            # raw integer beside the flag
])
def test_confirmatory_refusals_in_process(argv: list[str], set_env: bool, tmp_path: Path,
                                          monkeypatch: pytest.MonkeyPatch,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    """The flag with ``--seed-id`` or a raw seed, or without variables, is refused (64).

    Reference: the refusal contract. One stderr line, nothing created, no seed or salt echoed.
    """
    if set_env:
        monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
        monkeypatch.setenv("LPC_CONF_SALT", SALT)
    out = tmp_path / "out"
    code = main([*argv, "--out", str(out)], ledger_path=ledger_with(tmp_path / "l.jsonl", SEED))
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and err.startswith(PREFIX)
    assert not out.exists()
    assert str(SEED) not in err and SALT not in err


class _FakeStudy:
    """Stands in for ``Study``: no computation."""

    core_cells: dict = {}
    estimator_log: list = []

    def __init__(self, config: object, out_dir: Path) -> None:
        self.config = config


def run_with_fakes(argv: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                   **kwargs: Path) -> list[dict]:
    """Run ``main`` with the study replaced by fakes; return a deep copy of every save."""
    import copy
    import lpcstudy.__main__ as cli
    saves: list[dict] = []
    monkeypatch.setattr(cli, "Study", _FakeStudy)
    monkeypatch.setattr(cli, "run_system", lambda study, system: {"seed_seen": study.config.seed})
    monkeypatch.setattr(cli, "run_handling", lambda study, results: {"schema": "fake"})
    monkeypatch.setattr(cli, "verdicts", lambda results, config: {})
    monkeypatch.setattr(cli, "save_json", lambda obj, path: saves.append(copy.deepcopy(obj))
                        or path.write_text(json.dumps(obj)))
    monkeypatch.setattr(cli, "write_markdown", lambda *a: None)
    monkeypatch.setattr(cli, "make_figures", lambda *a: None)
    assert main([*argv, "--out", str(tmp_path / "out"), "--skip-robustness"], **kwargs) == 0
    return saves


def test_provenance_is_saved_incomplete_first_and_complete_last(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first incremental save holds the block with ``complete`` false, the last true.

    Reference: the plan (written from the first incremental ``save_json``, finished before the
    final save). The study is faked; the seed the study saw is the DEV-0 literal 20261005.
    """
    saves = run_with_fakes(["--preset", "smoke"], tmp_path, monkeypatch)
    first, last = saves[0]["provenance"], saves[-1]["provenance"]
    assert first["complete"] is False and first["end_utc"] is None
    assert last["complete"] is True and last["wall_seconds"] > 0 and last["peak_rss_bytes"] > 0
    assert last["seed_id"] == "DEV-0" and saves[-1]["config"]["seed_id"] == "DEV-0"
    assert saves[-1]["systems"]["lorenz63"]["seed_seen"] == 20261005 == saves[-1]["config"]["seed"]
    assert last["argv"][:2] == ["--preset", "smoke"]
    assert saves[-1]["handling"] == {"schema": "fake"}  # the run-level handling is saved (DEF-0001)
    assert "handling" not in saves[0]


def test_failed_platform_probe_is_logged_as_one_warning(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture) -> None:
    """A failed platform probe is recorded in the block and logged as one WARNING with a count (R2 wording).

    Reference: the plan (the caller counts and logs a failed probe; WU-0001.6). ``blas_record``
    is replaced by a failure; the faked study runs; the saved block keeps the error text and
    the log has exactly one warning naming 1 probe. Exact.
    """
    import lpcstudy.provenance as provenance_module
    monkeypatch.setattr(provenance_module, "blas_record",
                        lambda: {"libraries": [], "error": "OSError: no maps"})
    with caplog.at_level("WARNING", logger="lpcstudy"):
        saves = run_with_fakes(["--preset", "smoke"], tmp_path, monkeypatch)
    assert saves[-1]["provenance"]["blas"]["error"] == "OSError: no maps"
    warnings = [r.getMessage() for r in caplog.records if "platform probe" in r.getMessage()]
    assert warnings == ["1 platform probe failure(s) or fallback(s), recorded in the provenance "
                        "block: blas: OSError: no maps"]


def test_confirmatory_run_writes_no_seed_value(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A faked confirmatory run uses the synthetic seed but saves it nowhere.

    Reference: the synthetic literal; the fake study records the seed it received (so the
    run did use it), while ``results.json`` text and every save omit it. Exact.
    """
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    saves = run_with_fakes(["--preset", "smoke", FLAG], tmp_path, monkeypatch,
                           ledger_path=ledger_with(tmp_path / "l.jsonl", SEED))
    assert saves[-1]["config"]["seed"] is None and saves[-1]["config"]["seed_id"] == "CONF-1"
    assert saves[-1]["provenance"]["label"] == "CONFIRMATORY: UNPROMOTED"
    assert saves[-1]["systems"]["lorenz63"]["seed_seen"] == SEED   # the fake received it
    text = (tmp_path / "out" / "smoke" / "results.json").read_text()
    assert text.count(str(SEED)) == 1       # only the fake's own 'seed_seen' echo
    del saves[-1]["systems"]
    assert str(SEED) not in json.dumps(saves[-1]) and SALT not in text


def test_mismatched_commitment_in_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    """A seed that differs from the committed one is refused (64) with one line."""
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED + 1))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    out = tmp_path / "out"
    code = main([FLAG, "--out", str(out)], ledger_path=ledger_with(tmp_path / "l.jsonl", SEED))
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and err.startswith(PREFIX)
    assert not out.exists() and str(SEED + 1) not in err and SALT not in err


BASELINE_SMOKE = Path("/home/brianm/projects/physics/chaos/lpcstudy/runs/baseline/smoke/results.json")


def _stale_results(tmp_path: Path) -> Path:
    """A synthetic pre-WU-0002.2 results file (v1 keys) at ``tmp_path/out/smoke``."""
    path = tmp_path / "out" / "smoke" / "results.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"config": {}, "systems": {"lorenz63": {
        "H1a": {"pass": True}, "H1e": {"pass": True}, "H1f": {"pass": False},
        "H3b": {"pass": True}, "H3d": {"pass": True}}}}))
    return path


def _assert_stale_refused(path: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``--report-only`` on ``path`` returns 64 with one line and leaves every file untouched."""
    before = path.read_bytes()
    assert main(["--preset", "smoke", "--out", str(tmp_path / "out"), "--report-only"]) == 64
    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == "" and len(lines) == 1
    assert lines[0].startswith("lpcstudy: refused (stale results schema): ")
    assert "older than WU-0002.2" in lines[0]
    assert path.read_bytes() == before
    assert sorted(p.name for p in path.parent.iterdir()) == ["results.json"]


def test_report_only_refuses_a_pre_v3_results_file_and_writes_nothing(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A results file with v1 keys is refused (exit 64, one line); the bytes stay identical.

    Reference: the decision-log correction table (the v1 keys H1e, H1f, H3d no longer exist, and
    the keys H1a to H1d, H3b, H3c changed meaning), and the CLI's refusal contract (exit 64, one
    stderr line, nothing created). The file is a synthetic stale dict; the comparison is of
    bytes before and after and of the directory listing. Exact, no tolerance.
    """
    _assert_stale_refused(_stale_results(tmp_path), tmp_path, capsys)


@pytest.mark.skipif(not BASELINE_SMOKE.exists(), reason="the v1 baseline smoke file is absent")
def test_report_only_refuses_the_v1_baseline_smoke_copy(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A tmp_path copy of the v1 baseline smoke ``results.json`` is refused and left identical.

    Reference: as above; the baseline (read-only, copied, never written) is a real v1 file with
    the keys H1e, H1f and H3d. Exact bytes.
    """
    path = tmp_path / "out" / "smoke" / "results.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(BASELINE_SMOKE.read_bytes())
    _assert_stale_refused(path, tmp_path, capsys)


def test_report_only_refuses_a_results_file_with_pass_flags_and_no_verdict(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A file from before WU-0002.9 (boolean ``pass``, no ``verdict``) is refused, nothing written.

    Reference (plan R3): the CLI's refusal contract (exit 64, one stderr line, no file created or
    changed) and v3 section 7 (a boolean cannot say inconclusive, so it is not relabelled). The
    file has v3 keys (so it passes the identifier check) with only ``pass``. Exact bytes.
    """
    path = tmp_path / "out" / "smoke" / "results.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"config": {}, "systems": {"lorenz63": {
        "H1a": {"pass": True}, "H2a": {"pass": False}}}}))
    before = path.read_bytes()
    assert main(["--preset", "smoke", "--out", str(tmp_path / "out"), "--report-only"]) == 64
    captured = capsys.readouterr()
    lines = captured.err.splitlines()
    assert captured.out == "" and len(lines) == 1
    assert lines[0].startswith("lpcstudy: refused (stale results schema): ")
    assert "no verdict" in lines[0] and "WU-0002.9" in lines[0]
    assert path.read_bytes() == before
    assert sorted(p.name for p in path.parent.iterdir()) == ["results.json"]


def test_report_only_accepts_a_current_results_file(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A results file with v3 keys and verdicts gets its verdicts rewritten and the report built.

    Reference: the identifier table (H1a, H2a are v3 keys) and v3 section 7. The report writers
    are replaced by recorders, so only the check and the verdict step are exercised. The file
    carries ``verdict`` keys (a plan-listed edit of this test, which carried ``pass`` only). The
    smoke config runs one system, so a pass reads "inconclusive" with the other two v3 systems
    missing, and a fail reads "not supported". Exact.
    """
    import lpcstudy.__main__ as cli
    path = tmp_path / "out" / "smoke" / "results.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"config": {}, "systems": {"lorenz63": {
        "H1a": {"verdict": "pass", "pass": True}, "H2a": {"verdict": "fail", "pass": False}}}}))
    built: list[str] = []
    monkeypatch.setattr(cli, "write_markdown", lambda *a: built.append("md"))
    monkeypatch.setattr(cli, "make_figures", lambda *a: built.append("fig"))
    assert main(["--preset", "smoke", "--out", str(tmp_path / "out"), "--report-only"]) == 0
    saved = json.loads(path.read_text())
    assert saved["verdicts"]["H1a"] == {"by_system": {"lorenz63": "pass"},
                                        "verdict": "inconclusive",
                                        "missing_systems": ["rossler", "chua"]}
    assert saved["verdicts"]["H2a"]["by_system"] == {"lorenz63": "fail"}
    assert saved["verdicts"]["H2a"]["verdict"] == "not supported"
    assert built == ["md", "fig"]


# ------------------------------------------------ WU-0005.6a: --estimator-refine-steps (K1)
# Reference for every test below: the contract of the plan and its Mathematics check, written
# before the code: the flag is an integer of at least 1 (canonical decimal), absent means the
# preset's value (15, the design), the sealed flag refuses it before the sealed seed is read, and
# --report-only refuses a value that differs from the stored one. Exact: exit codes, strings,
# dict equality. The study is faked (``run_with_fakes``) and never run.
STEPS_FLAG = "--estimator-refine-steps"


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "x", "", " 15", "15 ", "015", "+15", "1e1",
                                   "٣", "1000", "999999999", "9" * 5000])
def test_k1_bad_refine_value_is_refused_without_echo(value: str, tmp_path: Path,
                                                      capsys: pytest.CaptureFixture[str]) -> None:
    """K1: 0, -1, 1.5, x, "" and the other non-canonical forms give 64, one line, nothing created.

    The value is not echoed (a refusal line names the flag, never the value). Both the separate
    and the ``=`` form are covered.
    """
    for argv in ([STEPS_FLAG, value], [f"{STEPS_FLAG}={value}"]):
        out = tmp_path / "out"
        code = main([*argv, "--preset", "smoke", "--out", str(out)])
        captured = capsys.readouterr()
        lines = captured.err.splitlines()
        assert code == 64 and captured.out == ""
        assert len(lines) == 1 and lines[0].startswith(PREFIX) and STEPS_FLAG in lines[0]
        if value.strip():
            assert value not in lines[0].replace(STEPS_FLAG, "")
        assert not out.exists()


@pytest.mark.parametrize("order", ["flag-first", "flag-last"])
def test_k1_refine_with_the_sealed_flag_is_refused_before_the_sealed_seed(
        order: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """K1: the sealed flag with the knob gives 64 in either order, and the ledger is never read.

    Reference: the plan ("refused together with the sealed flag"). The ledger path does not
    exist and valid-looking variables are set: if the sealed seed were read, the refusal would be
    about the ledger and not about the knob (the line must name the knob), and the seed and the
    salt must not appear in the line.
    """
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    argv = [FLAG, STEPS_FLAG, "30"] if order == "flag-first" else [STEPS_FLAG, "30", FLAG]
    out = tmp_path / "out"
    code = main([*argv, "--out", str(out)], ledger_path=tmp_path / "missing_ledger.jsonl")
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and err.startswith(PREFIX)
    assert STEPS_FLAG in err and "confirmatory flag" in err
    assert str(SEED) not in err and SALT not in err and not out.exists()


def test_k1_choose_refine_steps_values() -> None:
    """``choose_refine_steps``: absent gives None; 15, 30 and 60 give the integers; 1 is allowed."""
    from lpcstudy.__main__ import choose_refine_steps
    parse = lambda argv: choose_refine_steps(build_parser().parse_args(argv))
    assert parse([]) is None
    assert [parse([STEPS_FLAG, text]) for text in ("1", "15", "30", "60", "120", "240", "999")] == [
        1, 15, 30, 60, 120, 240, 999]
    assert parse([f"{STEPS_FLAG}=30"]) == 30


def _fake_config(argv: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    """The ``config`` record of the last save of a faked run."""
    return run_with_fakes(argv, tmp_path, monkeypatch)[-1]["config"]


def test_k1_flag_sets_only_the_budget(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """K1: absent is the preset's 15; ``15`` changes nothing; ``30`` changes that one key only.

    Reference: the preset (``PRESETS["smoke"]``, 15 by the design of v3 section 4) and the
    ``dataclasses.asdict`` of the config; dict equality is exact, and the provenance argv carries the
    flag so the run is self-describing.
    """
    from lpcstudy.config import PRESETS
    absent = _fake_config(["--preset", "smoke"], tmp_path / "a", monkeypatch)
    assert absent["estimator_refine_steps"] == PRESETS["smoke"].estimator_refine_steps == 15
    same = _fake_config(["--preset", "smoke", STEPS_FLAG, "15"], tmp_path / "b", monkeypatch)
    assert same == absent
    thirty = _fake_config(["--preset", "smoke", STEPS_FLAG, "30"], tmp_path / "c", monkeypatch)
    assert thirty["estimator_refine_steps"] == 30
    assert {k: v for k, v in thirty.items() if k != "estimator_refine_steps"} == {
        k: v for k, v in absent.items() if k != "estimator_refine_steps"}
    saves = run_with_fakes(["--preset", "smoke", STEPS_FLAG, "60"], tmp_path / "d", monkeypatch)
    assert saves[-1]["provenance"]["argv"][:4] == ["--preset", "smoke", STEPS_FLAG, "60"]


def test_k1_flag_reaches_the_study_and_keeps_the_systems_option(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The ``Study`` receives the replaced config, whatever the order of ``--systems``."""
    import lpcstudy.__main__ as cli
    seen: list = []

    class Recorder(_FakeStudy):
        def __init__(self, config: object, out_dir: Path) -> None:
            super().__init__(config, out_dir)
            seen.append(config)

    run_with_fakes(["--preset", "smoke", "--systems", "lorenz63", STEPS_FLAG, "30"],
                   tmp_path, monkeypatch)
    monkeypatch.setattr(cli, "Study", Recorder)
    assert main(["--preset", "smoke", STEPS_FLAG, "30", "--systems", "lorenz63", "--out",
                 str(tmp_path / "e"), "--skip-robustness"]) == 0
    assert seen[-1].estimator_refine_steps == 30 and seen[-1].core_systems == ("lorenz63",)


def _stored_results(tmp_path: Path, steps: int | None) -> Path:
    """A current-schema results file whose config stores ``steps`` (no key if ``None``)."""
    path = tmp_path / "out" / "smoke" / "results.json"
    path.parent.mkdir(parents=True)
    config = {} if steps is None else {"estimator_refine_steps": steps}
    path.write_text(json.dumps({"config": config, "systems": {"lorenz63": {
        "H1a": {"verdict": "pass", "pass": True}}}}))
    return path


@pytest.mark.parametrize(("stored", "argv_steps", "accepted"), [
    (30, "30", True), (15, "15", True), (15, None, True), (None, None, True),
    (30, "15", False), (15, "30", False), (None, "30", False), (30, None, False)])
def test_k1_report_only_needs_the_stored_budget(
        stored: int | None, argv_steps: str | None, accepted: bool, tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """K1: ``--report-only`` accepts the stored budget and refuses a different one (exit 64).

    Reference: the plan ("must equal results[config][estimator_refine_steps], a mismatch is
    refused") and, for the rows with the flag absent and a stored 30, the report's label: it prints
    the budget from the config (``iterative_label``), so a stored 30 under the preset's 15 would be
    mislabelled, and is refused too. A file with no stored budget (older) and no flag passes as
    before. Refusals: one line, the file's bytes unchanged, no other file written.
    """
    import lpcstudy.__main__ as cli
    path = _stored_results(tmp_path, stored)
    built: list[str] = []
    monkeypatch.setattr(cli, "write_markdown", lambda *a: built.append("md"))
    monkeypatch.setattr(cli, "make_figures", lambda *a: built.append("fig"))
    before = path.read_bytes()
    argv = ["--preset", "smoke", "--out", str(tmp_path / "out"), "--report-only"]
    if argv_steps is not None:
        argv += [STEPS_FLAG, argv_steps]
    code = main(argv)
    captured = capsys.readouterr()
    if accepted:
        assert code == 0 and built == ["md", "fig"]
    else:
        lines = captured.err.splitlines()
        assert code == 64 and built == [] and len(lines) == 1 and lines[0].startswith(PREFIX)
        assert path.read_bytes() == before
        assert sorted(p.name for p in path.parent.iterdir()) == ["results.json"]


# ------------------------------------------------ WU-0003.7b: --states-dump
# Reference: the contract of the plan (B2 row .7b, b6) and of the knob it copies
# (``--estimator-refine-steps``): opt-in, refused with the sealed flag before the sealed seed is
# read, refused with --report-only, one provenance leaf and nothing else when on. Exact (exit
# codes, strings, dict equality); the study is faked.
DUMP_FLAG = "--states-dump"


@pytest.mark.parametrize("order", ["flag-first", "flag-last"])
def test_states_dump_with_the_sealed_flag_is_refused_before_the_sealed_seed(
        order: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """b6: the sealed flag with the dump gives 64 in either order, one line, nothing created.

    The ledger path does not exist and valid-looking variables are set: if the sealed seed were
    read first, the refusal would be about the ledger; the line must name the dump flag and say
    why, and the seed and salt must not appear in it.
    """
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    argv = [FLAG, DUMP_FLAG] if order == "flag-first" else [DUMP_FLAG, FLAG]
    out = tmp_path / "out"
    code = main([*argv, "--out", str(out)], ledger_path=tmp_path / "missing_ledger.jsonl")
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and err.startswith(PREFIX)
    assert DUMP_FLAG in err and "confirmatory flag" in err
    assert str(SEED) not in err and SALT not in err and not out.exists()


def test_states_dump_with_report_only_is_refused(tmp_path: Path,
                                                 capsys: pytest.CaptureFixture[str]) -> None:
    """--report-only recomputes nothing, so the dump flag is refused (not silently ignored)."""
    out = tmp_path / "out"
    code = main([DUMP_FLAG, "--report-only", "--preset", "smoke", "--out", str(out)])
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and DUMP_FLAG in err and "--report-only" in err
    assert not out.exists()


def test_choose_states_dump_values() -> None:
    """Absent gives False, present gives True; the flag takes no value."""
    from lpcstudy.__main__ import choose_states_dump
    parse = lambda argv: choose_states_dump(build_parser().parse_args(argv))
    assert parse([]) is False and parse([DUMP_FLAG]) is True
    with pytest.raises(SystemExit):
        build_parser().parse_args([f"{DUMP_FLAG}=1"])


def test_states_dump_on_adds_one_provenance_leaf_and_hands_the_study_a_dump(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Dump on: ``provenance.states_dump`` is True and ``study.dump`` is a ``StateDump``; off: neither.

    The study is faked and its ``dump`` attribute is read after the run. The
    saved results of the two runs are equal except that one provenance leaf (the dump off adds no
    leaf at all, b1).
    """
    from lpcstudy.dump import StateDump

    created: list[_FakeStudy] = []
    original = _FakeStudy.__init__
    monkeypatch.setattr(_FakeStudy, "dump", None, raising=False)
    monkeypatch.setattr(_FakeStudy, "__init__", lambda self, config, out_dir: (
        original(self, config, out_dir), created.append(self))[0])
    off = run_with_fakes(["--preset", "smoke"], tmp_path / "off", monkeypatch)
    on = run_with_fakes(["--preset", "smoke", DUMP_FLAG], tmp_path / "on", monkeypatch)
    assert created[0].dump is None and isinstance(created[1].dump, StateDump)
    assert "states_dump" not in off[-1]["provenance"] and on[-1]["provenance"]["states_dump"] is True
    drop = lambda block: {k: v for k, v in block.items() if k not in ("states_dump", "argv",
                                                                         "start_utc", "end_utc",
                                                                         "wall_seconds",
                                                                         "peak_rss_bytes")}
    assert drop(on[-1]["provenance"]).keys() == drop(off[-1]["provenance"]).keys()
    # wall-clock "seconds" differs between any two runs; everything else outside provenance is equal
    assert {k: v for k, v in on[-1].items() if k not in ("provenance", "seconds")} == \
        {k: v for k, v in off[-1].items() if k not in ("provenance", "seconds")}
