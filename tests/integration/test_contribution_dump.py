"""Phase J contribution library on a smoke state dump (WU-0048 (f1), (g)).

One smoke preset with ``--states-dump`` runs on the development seed DEV-0 on
the CPU, in a fresh process (the pattern of ``test_states_dump.py``). Then:

* (f1) ``contribution.check_stored_scores``: ``core/state_mse/<rule>`` is
  recomputed by the library's realized score from the dumped per-draw errors
  and weights (A0 to A4 at every evaluation horizon, A5 at ``H_ref``) within
  1e-12 relative. Reference: the run's own scores (``pipeline.score_rules``,
  an independent code path). Round-off of the recomputation: a blend, a
  square and a mean of ``E`` terms, a few ulps.
* (g) ``contribution.qn_cross_check``: the WU-0039b rows (b1) leave-one-out
  and (b2) Shapley, rebuilt from the dump's split arrays (oracle profile,
  ``w*(H_ref)`` from the full-grid moments, ``ln T`` from ``split/T``), equal
  the run's ``ablation/profile_conditions/oracle`` leaves. Reference: the
  leaves of ``results.json``. Tolerance: bitwise (the same function, the same
  inputs, the same resamples), so drop-N reproduces Q-N's procedure exactly.
* The tool ``tools/lpc_contrib.py`` on the smoke run writes ``contrib.json``
  and ``contrib.md`` with the DEVELOPMENT label before every table (its
  refusals are unit-tested in ``tests/unit/test_tools_lpc_contrib.py``).

WU-0049 (experiments C and E) adds, on the same dump:

* the realized horizon of a blend (``joint_decisions.realized_policy_horizon``)
  reproduces the run's stored Kaplan-Meier aggregates exactly for the A0,
  A1, A2 and A4 weights;
* the characteristic crossing time of a policy on the dumped curves:
  ``T - 1 <= T_c <= T`` and ``ceil(T_c)`` equals
  ``oracle.characteristic_horizon`` except where ``e_{T-1} = theta`` (counted);
* ``tools/lpc_contrib_ce.py`` on the smoke run (after ``lpc_contrib.py``):
  labeled tables, and figures that ``--figures-from`` regenerates byte for
  byte.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from lpcstudy import contribution as cb

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 600
SYSTEM = "lorenz63"


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    """Run the smoke preset with the dump once; return the run folder."""
    out = tmp_path_factory.mktemp("contrib") / "run"
    env = {
        **os.environ,
        "JAX_PLATFORMS": "cpu",
        "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
    }
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "lpcstudy",
            "--preset",
            "smoke",
            "--seed-id",
            "DEV-0",
            "--out",
            str(out),
            "--states-dump",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
    )
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-15:])
    assert done.returncode == 0, tail
    run = out / "smoke"
    results = json.loads((run / "results.json").read_text())
    with np.load(run / "states" / f"{SYSTEM}.npz", allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    return {"run": run, "results": results, "arrays": arrays}


def test_f1_stored_scores_are_recomputed_from_the_per_draw_errors(
    smoke,
) -> None:
    """(f1): every stored per-state MSE within 1e-12 relative."""
    data = cb.SystemData.from_arrays(smoke["arrays"])
    record = cb.check_stored_scores(data)
    assert record["within_1e-12"], record
    assert set(record["max_rel_diff"]) == {"A0", "A1", "A2", "A3", "A4", "A5"}


def test_g_wu0039b_profile_rows_are_reproduced_bitwise_from_the_dump(
    smoke,
) -> None:
    """(g): drop-one (b1) and Shapley (b2) rows equal the run's leaves."""
    cfg = smoke["results"]["config"]
    data = cb.SystemData.from_arrays(smoke["arrays"])
    mine = cb.qn_cross_check(
        data,
        int(cfg["seed"]),
        int(cfg["bootstrap_resamples"]),
        int(cfg["bootstrap_block"]),
    )
    leaves = smoke["results"]["systems"][SYSTEM]["ablation"][
        "profile_conditions"
    ]["oracle"]
    for target, entry in mine.items():
        theirs = leaves[target]
        for x, row in entry["leave_one_out"].items():
            got = theirs["leave_one_out"][x]
            assert row["delta_r2"] == got["delta_r2"], (target, x)
            assert list(row["ci"]) == list(got["ci"]), (target, x)
            assert row["reading"] == got["reading"], (target, x)
            assert row["n_failed_resamples"] == got["n_failed_resamples"]
        for x, row in entry["shapley"].items():
            assert row["share"] == theirs["shapley"][x]["share"], (target, x)
            assert list(row["ci"]) == list(theirs["shapley"][x]["ci"])
        assert entry["r2_by_subset"] == theirs["r2_by_subset"], target


def test_tool_writes_labeled_tables_on_the_smoke_run(smoke, tmp_path) -> None:
    """The CLI on the smoke run: (f1) and (g) pass, every table is labeled."""
    tool = REPO_ROOT / "tools" / "lpc_contrib.py"
    run = smoke["run"]
    env = {**os.environ, "JAX_PLATFORMS": "cpu"}
    out = tmp_path / "out"
    done = subprocess.run(
        [
            sys.executable,
            "-I",
            str(tool),
            str(run),
            "--out",
            str(out),
            "--jobs",
            "4",
        ],
        capture_output=True,
        env=env,
        timeout=TIMEOUT_SECONDS,
    )
    assert done.returncode == 0, done.stderr.decode()[-2000:]
    record = json.loads((out / "contrib.json").read_text())
    label = "DEVELOPMENT (DEV-0): exploratory, not a hypothesis test"
    assert record["label"] == label
    system = record["systems"][SYSTEM]
    assert system["checks"]["f1_state_mse"]["within_1e-12"]
    assert system["checks"]["g_wu0039b"]["all_rows_reproduced"]
    text = (out / "contrib.md").read_text()
    blocks = text.split("\n\n")
    tables = [b for b in blocks if b.lstrip().startswith("|")]
    assert tables
    for i, block in enumerate(blocks):
        if block.lstrip().startswith("| horizon") or block.lstrip().startswith(
            "| profile"
        ):
            assert label in blocks[i - 1] or label in blocks[i - 2], block[:80]


# ----------------------------------------------------------------- WU-0049
def _policy_weights(a: dict) -> dict[str, np.ndarray]:
    """A0, A1, A2 (rebuilt on 1..H_max) and A4 on the full grid."""
    from lpcstudy import joint_decisions as jd

    e_c = a["split/test/cp_err_full"]
    con = "split/construction"
    a2 = jd.pooled_weight(a[f"{con}/E_C"], a[f"{con}/E_P"], a[f"{con}/C"])
    a4 = a["split/test/a4_weight"]
    assert np.all(a4 == a4[:, :, :1])
    return {
        "A0": np.ones_like(e_c),
        "A1": np.zeros_like(e_c),
        "A2": np.broadcast_to(a2, e_c.shape),
        "A4": np.broadcast_to(a4[:, :, :1], e_c.shape),
    }


def test_realized_policy_horizon_reproduces_the_stored_km_aggregates(
    smoke,
) -> None:
    """The realized horizon of a blend, given A0 to A4 weights, gives the
    run's Kaplan-Meier median, restricted mean and curve exactly.

    Reference: ``scores/<rule>/km_median_lyapunov``, ``rmst_lyapunov`` and
    ``km_curves/<rule>`` of ``results.json`` (``pipeline.score_rules``, the
    run's own code path). The rebuilt A2 equals the dumped A2 bitwise at the
    evaluation horizons. Tolerance: exact (the same float64 operations on
    the same arrays; the JSON floats round-trip exactly).
    """
    from lpcstudy import joint_decisions as jd
    from lpcstudy.statistics import kaplan_meier

    a = smoke["arrays"]
    res = smoke["results"]["systems"][SYSTEM]
    theta = float(a["meta/horizon_threshold"])
    lt = int(a["meta/steps_per_lyapunov"])
    h_max = a["split/test/cp_err_full"].shape[-1]
    weights = _policy_weights(a)
    cols = a["core/horizons"] - 1
    a2 = weights["A2"][:, :, cols]
    assert np.array_equal(a2, a["split/test/a2_weight"])
    for rule, w in weights.items():
        durations, events = jd.realized_policy_horizon(
            w,
            a["split/test/cp_err_full"],
            a["split/test/plp_err_full"],
            a["split/test/verify_noise"],
            theta,
        )
        curve = kaplan_meier(durations, events, h_max)
        stored = res["scores"][rule]
        assert curve.median() / lt == stored["km_median_lyapunov"], rule
        assert curve.restricted_mean() / lt == stored["rmst_lyapunov"], rule
        assert curve.survival.tolist() == res["km_curves"][rule], rule


def test_policy_crossing_on_the_dumped_curves(smoke) -> None:
    """``T - 1 <= T_c <= T``; ``ceil(T_c)`` is ``characteristic_horizon``.

    Policies A0, A1, A2 and A4 on the test moments ``(n, H_max)``.
    Reference: ``oracle.characteristic_horizon`` of ``oracle.hybrid_mse``
    with the same weights (the production code). ``T_c = T - 1`` occurs only
    where ``e_{T-1} = theta`` exactly, which is counted and is the only
    place where the ceiling may differ. Tolerance: exact.
    """
    from lpcstudy import joint_decisions as jd
    from lpcstudy.ensemble import EnsembleMoments
    from lpcstudy.oracle import characteristic_horizon, hybrid_mse

    a = smoke["arrays"]
    noise = float(a["meta/core_noise"])
    theta = float(a["meta/horizon_threshold"])
    horizons = a["meta/horizons_full"]
    e_c, e_p, c = (a[f"split/test/{k}"] for k in ("E_C", "E_P", "C"))
    moments = EnsembleMoments(
        horizons=horizons,
        mean_cp=np.zeros_like(e_c),
        mean_plp=np.zeros_like(e_c),
        sq_cp=e_c,
        sq_plp=e_p,
        cross=c,
        analog_seed=np.ones(len(e_c)),
        est_seed=np.ones(len(e_c)),
        noise_sens=np.ones(len(e_c)),
    )
    for rule, w in _policy_weights(a).items():
        cross = jd.policy_crossing(e_c, e_p, c, w, noise, theta)
        for j in range(w.shape[1]):
            first, event = characteristic_horizon(
                hybrid_mse(moments, w[:, j, :]), horizons, noise, theta
            )
            np.testing.assert_array_equal(cross.T[:, j], first, err_msg=rule)
            np.testing.assert_array_equal(cross.event[:, j], event)
            fin = np.isfinite(cross.T_c[:, j])
            t_c, t = cross.T_c[fin, j], first[fin]
            assert np.all((t - 1 <= t_c) & (t_c <= t)), rule
            differs = np.ceil(t_c) != t
            np.testing.assert_array_equal(differs, cross.exact[fin, j])
        assert cross.n_exact_theta == int(cross.exact.sum())


def test_ce_tool_writes_labeled_tables_and_reproducible_figures(
    smoke, tmp_path
) -> None:
    """``lpc_contrib.py`` then ``lpc_contrib_ce.py`` on the smoke run.

    Exit 0; the DEVELOPMENT label before every table; the refit allocation
    reproduces the A/D record's MSE exactly (the same job and seed); the
    figures regenerate byte for byte from ``ce.json`` (``--figures-from``).
    """
    run = smoke["run"]
    env = {**os.environ, "JAX_PLATFORMS": "cpu"}
    tools = REPO_ROOT / "tools"

    def call(*argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", *argv],
            capture_output=True,
            env=env,
            timeout=TIMEOUT_SECONDS,
        )

    abd = tmp_path / "abd"
    done = call(str(tools / "lpc_contrib.py"), str(run), "--out", str(abd))
    assert done.returncode == 0, done.stderr.decode()[-2000:]
    out = tmp_path / "ce"
    done = call(
        str(tools / "lpc_contrib_ce.py"),
        str(run),
        "--out",
        str(out),
        "--abd",
        str(abd / "contrib.json"),
        "--jobs",
        "4",
    )
    assert done.returncode == 0, done.stderr.decode()[-2000:]
    record = json.loads((out / "ce.json").read_text())
    label = "DEVELOPMENT (DEV-0): exploratory, not a hypothesis test"
    assert record["label"] == label
    system = record["systems"][SYSTEM]
    assert system["checks"]["g_reproduces_abd_max_abs"] == {
        "oracle": 0.0,
        "deployable": 0.0,
    }
    for key in ("C1", "C2", "C3", "E_H2a", "E_H2e", "E_H3c"):
        assert key in system, key
    text = (out / "ce.md").read_text()
    blocks = text.split("\n\n")
    tables = [i for i, b in enumerate(blocks) if b.lstrip().startswith("|")]
    assert tables
    for i in tables:
        assert label in blocks[i - 1], blocks[i][:80]
    digests = json.loads((out / "figures.sha256.json").read_text())
    again = call(
        str(tools / "lpc_contrib_ce.py"),
        "--figures-from",
        str(out / "ce.json"),
        "--out",
        str(tmp_path / "again"),
    )
    assert again.returncode == 0, again.stderr.decode()[-2000:]
    assert json.loads(again.stdout) == digests
    for name in digests:
        assert (out / "figures" / name).read_bytes() == (
            tmp_path / "again" / "figures" / name
        ).read_bytes()
