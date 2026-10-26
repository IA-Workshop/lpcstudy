"""End-to-end check of the optional state dump on the smoke preset (WU-0003.7b).

With the flag ``--states-dump`` a run also saves the raw per-state arrays behind
its summary numbers (error moments, weights, estimator results) in an ``.npz``
file, so a reader can recompute any reported number from the saved arrays. The
dump must change nothing else, and the saved arrays must really be what the run
used. This module runs the smoke preset (a small, fast version of the study)
twice on the development seed DEV-0 on the CPU, each time in a fresh Python
process: once without and once with ``--states-dump``. Each run is a preset, so
the file is run only when the preset slot is free. The numbering b1 to b7
follows the plan (B2 row .7b). Check b1 (dump off against the .7a tip: 0
changed, 0 removed, 0 added) needs a run of that older commit and is done by
hand with ``tools/leafdiff.py``; it is in the unit Log.

* b2: the ``results.json`` files of the two runs are bitwise equal (floats
  compared by their IEEE bytes), except that the dump run's ``provenance`` block
  has the extra leaf ``states_dump`` (and its own command line). Reference: the
  comparison in ``tools/leafdiff.py``, which excludes ``provenance`` and
  ``seconds``, and the provenance blocks compared here by hand.
* b3: the production summary function applied to each dumped array reproduces
  its leaf in the results. The summaries are the V4 median and mean absolute
  deviation, the Q-N Delta R^2 (``analysis.delta_r2``), the H1b PLP slope
  (``statistics.ols_slope``), the median weight profile and the H2b median
  weights, the per-rule MSE at ``H_ref`` and the cell's Levenberg-Marquardt
  block (``pipeline.lm_block``). The match is bitwise where the function and the
  order of operations are the same (V4, Q-N, H1b, weight profile, H2b, LM). The
  per-rule MSE leaf is the mean over all (state, draw) pairs while the dump
  holds per-state means, so it is compared to ``2 n E 2**-52`` relative. The
  reason: the worst-case relative error of a sum of ``n E`` positive terms is
  ``gamma_{nE}``, about ``n E 2**-53``, and the two orders of summation can
  differ by twice that.
* b3 also: the clip and replacement counts. The core cell's record pools the
  three data splits, so the per-split ``handling/<split>/`` arrays are summed
  and compared exactly with
  ``handling/cells/<core>/by_kind/<oracle|eval>/counts`` (the eight ``handled``
  columns and the three clipped-entry totals).
* b3 also, schema /2 (WU-0003.7c; a **dump-fidelity check**: the reference is
  the production statistic itself, so it proves that the dump holds what the run
  used, not that H1c or H1a is right): ``analysis.h1c_ratio_block`` applied to
  the dumped per-state H1c ratios of the eligible states reproduces the PLP and
  CP leaves (bitwise). The H1a medians ``median_seed_by_n_lib``, the reference
  ``inverse_dim_reference`` and, with the production generator labels, the fit
  statistics ``ratio`` and ``fitted_inverse_dim`` are reproduced from the dumped
  squared seed errors (bitwise).
* b4: ``(m_A + m_B) / 2 = m`` for ``E_C``, ``E_P`` and ``C`` (mean squared
  errors of CP and PLP, and their cross moment) at every evaluation horizon of
  the core cell and at ``H_ref`` of every sweep cell. Here ``m_A`` and ``m_B``
  are the moments from the two halves of the draws. The tolerance is ``1e-13``
  times the exact mean absolute term: the moment itself for the two squares
  (their terms are positive) and the dumped ``abs_C`` (the mean of ``|e_C e_P|``
  over the draws) for the cross moment. This is the plan's scale.
* b5: the median of the per-state V4 half-widths at ``H_ref`` equals the V4
  leaf, bitwise.
* b7: the file size is printed (the Log records it).
* Schema /3 (WU-0046), ``test_schema3_*``: criterion (iv), the dumped
  construction arrays are what the fit used, bitwise: A2 recomputed from the
  dumped full-grid construction moments equals the dumped A2 weight, and A3
  retrained from the dumped ``a3_train/`` arrays with the production generator
  labels has the run's ``allocator_digest``. The oracle profile is recomputed
  from the dumped ``eps_s``, ``delta``, ``Lambda_bar`` and ``N``; the test split
  lines up with Q-N, ``core/`` and the sweep groups.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 600
SYSTEM = "lorenz63"
CORE_CELL = "base|rho=0.01|n_lib=10000|core"

_SPEC = importlib.util.spec_from_file_location(
    "leafdiff", REPO_ROOT / "tools" / "leafdiff.py"
)
assert _SPEC is not None and _SPEC.loader is not None
leafdiff = importlib.util.module_from_spec(_SPEC)
sys.modules["leafdiff"] = leafdiff
_SPEC.loader.exec_module(leafdiff)


def run_smoke(out: Path, *flags: str) -> Path:
    """Run the smoke preset in a fresh CPU process, adding any extra ``flags``.

    Returns the folder that holds the run's output.
    """
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
            "--out",
            str(out),
            *flags,
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
    )
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-15:])
    assert (
        done.returncode == 0
    ), f"smoke {flags} exited {done.returncode}:\n{tail}"
    return out / "smoke"


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Run the smoke preset without and with the dump, once for the whole
    module.

    Returns the two output folders, the two parsed ``results.json`` trees and
    the arrays loaded from the dump.
    """
    base = tmp_path_factory.mktemp("states_dump")
    off = run_smoke(base / "off")
    on = run_smoke(base / "on", "--states-dump")
    results = {
        name: json.loads((path / "results.json").read_text())
        for name, path in (("off", off), ("on", on))
    }
    with np.load(on / "states" / f"{SYSTEM}.npz", allow_pickle=False) as loaded:
        arrays = {key: loaded[key] for key in loaded.files}
    return {"off": off, "on": on, "results": results, "arrays": arrays}


def test_b2_dump_on_equals_dump_off_except_the_provenance_leaf(runs) -> None:
    """b2: no leaf differs, is added or is removed; only the provenance block
    shows the flag.
    """
    off, on = runs["results"]["off"], runs["results"]["on"]
    outcome = leafdiff.compare(leafdiff.flatten(off), leafdiff.flatten(on))
    assert (
        outcome["different"] == []
        and outcome["added"] == []
        and outcome["removed"] == []
    )
    assert len(outcome["common"]) > 1000
    assert (
        "states_dump" not in off["provenance"]
        and on["provenance"]["states_dump"] is True
    )
    drop = (
        "states_dump",
        "argv",
        "start_utc",
        "end_utc",
        "wall_seconds",
        "peak_rss_bytes",
        "device_peak_bytes",
    )
    assert {k: v for k, v in on["provenance"].items() if k not in drop} == {
        k: v for k, v in off["provenance"].items() if k not in drop
    }
    assert not (runs["off"] / "states").exists()
    assert (runs["on"] / "states" / f"{SYSTEM}.npz").is_file()


def test_b3_the_production_summaries_of_the_dumped_arrays_reproduce_their_leaves(
    runs,
) -> None:
    """b3: the dumped arrays reproduce the V4, Q-N, H1b, H2b and LM leaves and
    the other summaries.

    The per-rule MSE agrees to the rounding bound ``gamma_nE`` described in the
    module docstring; the others agree bitwise.
    """
    from lpcstudy import analysis as an
    from lpcstudy.config import SMOKE
    from lpcstudy.pipeline import lm_block
    from lpcstudy.statistics import ols_slope

    a, res = runs["arrays"], runs["results"]["on"]["systems"][SYSTEM]
    ref_index = int(a["core/ref_index"])
    # V4 and b5
    for mi, m in enumerate(a["v4/M"].tolist()):
        leaf = res["validation"]["convergence"][str(m)]
        assert (
            float(np.median(a["v4/half_width"][mi, :, 0]))
            == leaf["median_half_width"]
        )
        assert (
            float(np.mean(np.abs(a["v4/signed_dev"][mi, :, 0])))
            == leaf["mean_abs_dev_from_max"]
        )
    assert bool(a["v4/extra_href_equal"]) is True
    # Q-N
    for kind in ("oracle", "deployable"):
        for target in ("logit_w_interior", "w_zero_indicator", "log_horizon"):
            key = f"qn/{kind}/{target}"
            rows = np.flatnonzero(a[f"{key}/domain"])
            got = an.delta_r2(
                a[f"{key}/y"], a[f"{key}/pred3"], a[f"{key}/pred4"], rows
            )
            assert got == res["Q-N"][kind][target]["delta_r2"], key
    # H1b PLP slope: x = log(g_H delta / sqrt(m)), y = 0.5 log(max(E_P, 1e-12)),
    # finite pairs
    x_all = np.log(a["core/g_H_ref"] * a["core/delta"] / np.sqrt(3))
    y_all = 0.5 * np.log(np.maximum(a["core/E_P"][:, ref_index], 1e-12))
    keep = np.isfinite(x_all) & np.isfinite(y_all)
    assert ols_slope(x_all[keep], y_all[keep]) == res["H1b"]["PLP"]["slope"]
    assert int(keep.sum()) == res["H1b"]["n_states"]
    # median, q25 and q75 of the oracle weight at the evaluation horizons
    profile = res["weight_profile"]
    for j, h in enumerate(a["core/horizons"].tolist()):
        col = a["core/w_star"][:, j]
        assert float(np.median(col)) == profile["median"][h - 1]
        assert float(np.percentile(col, 25)) == profile["q25"][h - 1]
        assert float(np.percentile(col, 75)) == profile["q75"][h - 1]
    # H2b: the median of w*(H_ref) of every noise cell
    for rho, median in res["H2b"]["noise"]["median_w_by_noise"].items():
        group = f"sweep/rho={float(rho):g}|n_lib={SMOKE.core_library}"
        assert float(np.median(a[f"{group}/w_star_href"])) == median, rho
    # per-rule MSE at H_ref: the mean of the per-state means, to 2 n E 2**-52
    # relative
    n_states, n_draws = a["core/state_mse/A0"].shape[0], a["core/R"].shape[1]
    for rule, score in res["scores"].items():
        mean_state = float(np.mean(a[f"core/state_mse/{rule}"][:, ref_index]))
        assert mean_state == pytest.approx(
            score["mse_href"], rel=2 * n_states * n_draws * 2.0**-52, abs=0.0
        ), rule
    # schema /2: H1c from the dumped per-state ratios, H1a from the dumped seed
    # errors
    # (dump-fidelity check: the reference is the production statistic itself)
    from lpcstudy.analysis import _median_fit_stats, h1c_ratio_block
    from lpcstudy.data import make_rng
    from lpcstudy.statistics import bootstrap_values

    assert str(a["meta/schema"]) == "lpcstudy.states/3"
    for name in ("PLP", "CP"):
        block = h1c_ratio_block(
            a[f"h1c/{name}/ratio"][a[f"h1c/{name}/eligible"]],
            SMOKE,
            SYSTEM,
            with_verdict=name == "PLP",
        )
        leaf = {
            k: v
            for k, v in res["H1c"][name].items()
            if k != "n_ineligible_states"
        }
        assert json.dumps(block, sort_keys=True) == json.dumps(
            leaf, sort_keys=True
        ), name
        assert (
            int((~a[f"h1c/{name}/eligible"]).sum())
            == res["H1c"][name]["n_ineligible_states"]
        )
    sizes, inverse = a["h1a/n_lib"], a["h1a/inverse_dim"]
    keep = np.isfinite(inverse)
    for rho in a["h1a/noise_levels"].tolist():
        keep &= np.isfinite(a[f"h1a/rho={rho:g}/seed_sq"]).all(axis=1)
    assert float(inverse[keep].mean()) == res["H1a"]["inverse_dim_reference"]
    assert int(keep.sum()) == res["H1a"]["n_states"]
    for rho in a["h1a/noise_levels"].tolist():
        leaf = res["H1a"]["by_noise"][f"{rho:g}"]
        kept = a[f"h1a/rho={rho:g}/seed_sq"][keep]
        assert {
            str(int(n)): float(np.sqrt(v))
            for n, v in zip(sizes, np.median(kept, axis=0))
        } == leaf["median_seed_by_n_lib"]
        point, _ = bootstrap_values(
            lambda idx: _median_fit_stats(kept, inverse[keep], sizes, idx),
            int(keep.sum()),
            SMOKE.bootstrap_resamples,
            SMOKE.bootstrap_block,
            make_rng(SMOKE.seed, SYSTEM, "bootstrap", "H1a", f"{rho:g}"),
        )
        same = lambda x, y: np.float64(x).tobytes() == np.float64(y).tobytes()
        assert same(point[0], leaf["ratio"]) and same(
            point[1], leaf["fitted_inverse_dim"]
        ), rho
    # the clip and replacement counts: the cell record pools the three splits
    from lpcstudy.ensemble import DRAW_COUNTERS, ENTRY_COUNTERS

    cell = runs["results"]["on"]["systems"][SYSTEM]["handling"]["cells"][
        CORE_CELL
    ]
    for kind in ("oracle", "eval"):
        counts = cell["by_kind"][kind]["counts"]
        for column, name in enumerate(DRAW_COUNTERS):
            assert (
                sum(
                    int(a[f"handling/{sp}/{kind}_handled"][:, column].sum())
                    for sp in ("construction", "calibration", "test")
                )
                == counts[name]
            ), (kind, name)
        for column, name in enumerate(ENTRY_COUNTERS):
            assert (
                sum(
                    int(a[f"handling/{sp}/{kind}_clip_entries"][column])
                    for sp in ("construction", "calibration", "test")
                )
                == counts[name]
            ), (kind, name)
    # the cell's Levenberg-Marquardt block, pooled over the three splits in the
    # run's order
    parts = {
        kind: [
            tuple(
                a[f"lm/{split}/{kind}_{name}"]
                for name in ("residual", "accepted", "late")
            )
            for split in ("construction", "calibration", "test")
        ]
        for kind in ("oracle", "eval")
    }
    block = lm_block(parts, SMOKE.core_noise, SMOKE.embedding_dim - 3)
    stored = runs["results"]["on"]["systems"][SYSTEM]["handling"]["cells"][
        CORE_CELL
    ]["lm"]
    assert json.dumps(block, sort_keys=True) == json.dumps(
        stored, sort_keys=True
    )


def test_b4_the_two_halves_average_to_the_full_moment(runs) -> None:
    """b4: the two halves of the draws average to the full moment, in the core
    and sweep cells.

    ``(m_A + m_B) / 2 = m`` to 1e-13 times the exact mean absolute term.
    """
    a = runs["arrays"]
    assert a["core/half_n_draws"].tolist() == [15, 15]
    groups = [("core/", None)] + [
        (f"{k.rsplit('/', 1)[0]}/", None)
        for k in a
        if k.startswith("sweep/") and k.endswith("/w_star_href")
    ]
    assert (
        len(groups) >= 4
    )  # the core and at least the three sweep cells of the smoke preset
    for prefix, _ in groups:
        assert a[f"{prefix}half_n_draws"].tolist() == [15, 15]
        scale = {
            "E_C": a[f"{prefix}E_C"],
            "E_P": a[f"{prefix}E_P"],
            "C": a[f"{prefix}abs_C"],
        }
        for name, bound in scale.items():
            mean_half = 0.5 * (a[f"{prefix}{name}_A"] + a[f"{prefix}{name}_B"])
            assert np.all(
                np.abs(mean_half - a[f"{prefix}{name}"]) <= 1e-13 * bound
            ), (prefix, name)


def test_the_key_tree_has_no_key_that_is_also_a_prefix_and_the_qn_inputs_exist(
    runs,
) -> None:
    """R6 and R10: no dumped key is the ``/`` prefix of another, and
    ``qn/<kind>/`` has its inputs.

    A key that is also the prefix of another would clash when the arrays are
    stored as a tree. Reference: the schema in ``lpcstudy/dump.py`` (names typed
    here). The check is exact.
    """
    keys = set(runs["arrays"])
    assert not any(
        other.startswith(key + "/") for key in keys for other in keys
    )
    for kind in ("oracle", "deployable"):
        for name in ("x_test", "w_star", "log_t"):
            assert f"qn/{kind}/{name}" in keys, (kind, name)
        for target in ("logit_w_interior", "w_zero_indicator", "log_horizon"):
            for name in ("pred3", "pred4", "y", "domain"):
                assert f"qn/{kind}/{target}/{name}" in keys, (
                    kind,
                    target,
                    name,
                )


def test_b7_the_dump_size_is_reported(runs) -> None:
    """b7: the size of the dump at smoke is reported and under 5 MB.

    The size is recorded in the unit Log, where the pilot and full sizes are
    also estimated.
    """
    path = runs["on"] / "states" / f"{SYSTEM}.npz"
    print(
        f"states dump size at smoke: {path.stat().st_size} bytes, {len(runs['arrays'])} arrays"
    )
    assert 0 < path.stat().st_size < 5_000_000


def test_schema3_construction_moments_and_a3_arrays_are_what_the_fit_used(
    runs,
) -> None:
    """Criterion (iv) of WU-0046: the dumped construction data are bitwise
    what A2 and A3 were fitted on.

    A3 trains on per-draw errors (the first ``K`` oracle draws at the
    allocator grid), not on moments; the moments of the construction split are
    what A2 (and the A5 targets) are fitted on. So (iv) is checked twice:

    * A2: ``clip(sum(E_P - C) / max(sum(E_C + E_P - 2 C), 1e-300), 0, 1)``
      over the dumped construction states at every allocator-grid horizon (the
      pooled minimizer, written here) equals the dumped A2 weight of the test
      draws at ``H_ref`` (one weight for all draws) and is the same number at
      the grid columns of the full-grid copy as at the grid itself.
    * A3: ``ErrorPredictor.fit`` on the dumped ``a3_train/`` arrays, the dumped
      grid, the core noise, width 64, the preset's epochs and the production
      generator ``make_rng(seed, system, D, "allocator")`` gives a network whose
      ``weights_digest`` is the run's ``fitted/allocator_digest`` (SHA-256 of
      the weights: any differing bit of the inputs would change it).

    Tolerance: exact (the same operations on the same float64 arrays, CPU).
    """
    from lpcstudy.allocation import ErrorPredictor
    from lpcstudy.config import SMOKE
    from lpcstudy.data import make_rng

    a, res = runs["arrays"], runs["results"]["on"]["systems"][SYSTEM]
    grid = a["meta/allocator_grid"]
    ref = int(a["meta/reference_horizon"])
    assert ref in grid.tolist()
    con = "split/construction"
    e_c, e_p, cross = a[f"{con}/E_C"], a[f"{con}/E_P"], a[f"{con}/C"]
    assert e_c.shape == (SMOKE.n_construction, SMOKE.horizon_max)
    numerator = np.sum(e_p - cross, axis=0)
    denominator = np.sum(e_c + e_p - 2.0 * cross, axis=0)
    a2 = np.clip(numerator / np.maximum(denominator, 1e-300), 0.0, 1.0)
    dumped = a["core/weight_href/A2"]
    assert np.all(dumped == dumped.flat[0])
    assert a2[ref - 1].tobytes() == dumped.flat[0].tobytes()
    kept = {
        k: a[f"{con}/a3_train/{k}"] for k in ("inputs", "cp_err", "plp_err")
    }
    assert kept["cp_err"].shape == (
        SMOKE.n_construction,
        SMOKE.allocator_draws,
        len(grid),
    )
    assert kept["inputs"].shape == (
        SMOKE.n_construction,
        SMOKE.allocator_draws,
        SMOKE.embedding_dim,
    )
    predictor = ErrorPredictor.fit(
        kept["inputs"],
        kept["cp_err"],
        kept["plp_err"],
        grid,
        float(a["meta/core_noise"]),
        width=64,
        epochs=SMOKE.allocator_epochs,
        rng=make_rng(SMOKE.seed, SYSTEM, SMOKE.embedding_dim, "allocator"),
    )
    assert (
        predictor.network.weights_digest() == res["fitted"]["allocator_digest"]
    )


def test_schema3_oracle_profile_horizon_and_alignment_on_the_smoke_dump(
    runs,
) -> None:
    """The ``split/`` group of the smoke dump is consistent with the run.

    References (independent of ``lpcstudy.dump``):

    * the oracle profile ``(ln eps_s/rho, ln delta/rho, Lambda_bar x 30,
      ln(N + 0.01))`` written here from the dumped columns, per split;
    * Q-N's own test arrays: ``qn/oracle/x_test`` and ``exp`` of
      ``qn/oracle/log_t`` (the profile and the horizon Q-N used);
    * ``core/E_C``, ``E_P``, ``C`` at the evaluation columns, and the sweep
      view of the core cell at ``H_ref`` for the first ``nS`` test states;
    * ``core/profile`` for the deployable test profile;
    * the evaluation inputs minus the clean delay vector, divided by ``rho``,
      are the standard normal query noise: every ``|z| < 6`` and the sample
      standard deviation is in [0.9, 1.1] (``n = 260 x 7`` values: the
      standard error of the s.d. is ``1/sqrt(2n) = 0.017``, so the band is
      six of them; ``P(|z| > 6) = 2e-9`` per value). This checks that
      ``delay_clean`` is the noise-free ``X_t`` of the same state, in the
      units of the inputs.

    Tolerance: exact except the noise band (Monte Carlo, stated above).
    """
    from lpcstudy.config import SMOKE

    a = runs["arrays"]
    rho = float(a["meta/core_noise"])
    assert rho == SMOKE.core_noise
    lt = int(a["meta/steps_per_lyapunov"])
    sizes = {
        "construction": SMOKE.n_construction,
        "calibration": SMOKE.n_calibration,
        "test": SMOKE.n_test,
    }
    z_all = []
    for split, n_s in sizes.items():
        g = f"split/{split}"
        assert a[f"{g}/state_index"].shape == (n_s,)
        assert np.all(np.diff(a[f"{g}/state_index"]) > 0)
        hand = np.column_stack(
            [
                np.log(a[f"{g}/eps_s"] / rho),
                np.log(a[f"{g}/delta"] / rho),
                a[f"{g}/Lambda_bar"] * lt,
                np.log(a[f"{g}/N"] + 0.01),
            ]
        )
        assert np.array_equal(a[f"{g}/profile_oracle"], hand), split
        t, censored = a[f"{g}/T"], a[f"{g}/T_censored"]
        assert np.all((t >= 1) & (t <= SMOKE.horizon_max))
        assert np.all(t[censored] == SMOKE.horizon_max)
        z = (a[f"{g}/delay_eval"] - a[f"{g}/delay_clean"][:, None, :]) / rho
        z_all.append(z.ravel())
    z = np.concatenate(z_all)
    assert np.all(np.abs(z) < 6.0) and 0.9 <= z.std() <= 1.1
    test = "split/test"
    assert np.array_equal(a[f"{test}/profile_oracle"], a["qn/oracle/x_test"])
    assert np.array_equal(np.log(a[f"{test}/T"]), a["qn/oracle/log_t"])
    assert np.array_equal(a[f"{test}/profile_deployable"], a["core/profile"])
    cols = a["core/horizons"] - 1
    for name in ("E_C", "E_P", "C"):
        assert np.array_equal(a[f"{test}/{name}"][:, cols], a[f"core/{name}"])
        sweep = f"sweep/rho={rho:g}|n_lib={SMOKE.core_library}/{name}"
        ref = int(a["meta/reference_horizon"])
        n_sweep = int(a["meta/n_test_sweep"])
        assert np.array_equal(a[f"{test}/{name}"][:n_sweep, ref - 1], a[sweep])
    assert a[f"{test}/a3_weight"].shape == (
        SMOKE.n_test,
        SMOKE.n_eval_draws,
        len(SMOKE.eval_horizons),
    )


def test_schema3_state_mse_is_recomputed_from_the_per_draw_errors_and_weights(
    runs,
) -> None:
    """Criterion (vi) of WU-0046b on the smoke dump (M-8, test (f1)).

    ``core/state_mse/<rule>`` is recomputed from the dumped per-draw errors
    against the noise-free truth (``split/test/cp_err``, ``plp_err``) and the
    dumped weights: A0 (weight 1) and A1 (weight 0), A2, A3 and A4
    (``split/test/<rule>_weight``) at every evaluation horizon, and A5 at
    ``H_ref`` (``core/weight_href/A5``). The formula
    ``(1/E) sum_j (w e_C + (1 - w) e_P)^2`` is written here. This is a
    dump-fidelity check: the stored values come from the same run, and the
    ``H_ref`` column of each is the score the verdicts use (checked bitwise by
    ``collect``, and against the results leaf by b3).

    Also checked, exactly: the shapes; the full-grid errors at the evaluation
    columns are the short arrays; the weights agree with the ``/2`` keys
    ``core/weight_href/<rule>`` at ``H_ref``, A2 is one number per horizon and
    A4 one per (state, draw); the full-grid half-draw moments at the
    evaluation columns are ``core/E_C_A`` and the others.

    Tolerance: ``1e-12`` relative, the criterion of the plan. The round-off of
    the recomputation is a few ulps (a blend, a square and a mean of ``E``
    terms: about ``(E + 3) 2**-53``, under ``1e-15`` at smoke), far below it.
    """
    from lpcstudy.config import SMOKE

    a = runs["arrays"]
    n, n_cal, e = SMOKE.n_test, SMOKE.n_calibration, SMOKE.n_eval_draws
    k, h_max = len(SMOKE.eval_horizons), SMOKE.horizon_max
    cols = a["core/horizons"] - 1
    ref_index = int(a["core/ref_index"])
    for split, n_s in (("test", n), ("calibration", n_cal)):
        for name in ("cp_err", "plp_err"):
            assert a[f"split/{split}/{name}"].shape == (n_s, e, k), split
            assert a[f"split/{split}/{name}"].dtype == np.float64, split
    for name in ("cp_err", "plp_err"):
        full = a[f"split/test/{name}_full"]
        assert full.shape == (n, e, h_max) and full.dtype == np.float64
        assert np.array_equal(full[:, :, cols], a[f"split/test/{name}"])
    weights = {
        rule: a[f"split/test/{rule.lower()}_weight"]
        for rule in ("A2", "A3", "A4")
    }
    for rule, w in weights.items():
        assert w.shape == (n, e, k) and w.dtype == np.float64, rule
        assert np.array_equal(
            w[:, :, ref_index], a[f"core/weight_href/{rule}"]
        ), rule
    assert np.all(weights["A2"] == weights["A2"][:1, :1, :])
    assert np.all(weights["A4"] == weights["A4"][:, :, :1])
    for name in ("E_C", "E_P", "C"):
        for tag in ("A", "B"):
            full = a[f"split/test/{name}_{tag}"]
            assert full.shape == (n, h_max), (name, tag)
            assert np.array_equal(full[:, cols], a[f"core/{name}_{tag}"])

    e_c, e_p = a["split/test/cp_err"], a["split/test/plp_err"]
    weights |= {"A0": np.ones_like(e_c), "A1": np.zeros_like(e_c)}
    for rule, w in weights.items():
        recomputed = ((w * e_c + (1.0 - w) * e_p) ** 2).mean(axis=1)
        np.testing.assert_allclose(
            recomputed, a[f"core/state_mse/{rule}"], rtol=1e-12, atol=0.0
        )
    w5 = a["core/weight_href/A5"]
    recomputed = (
        (w5 * e_c[:, :, ref_index] + (1.0 - w5) * e_p[:, :, ref_index]) ** 2
    ).mean(axis=1)
    np.testing.assert_allclose(
        recomputed, a["core/state_mse/A5"][:, ref_index], rtol=1e-12, atol=0.0
    )
