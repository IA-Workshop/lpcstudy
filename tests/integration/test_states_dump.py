"""The opt-in state dump on the smoke preset (WU-0003.7b; B2 row .7b, b2 to b5, b7).

Two smoke runs on DEV-0 in fresh interpreters, CPU: one without and one with ``--states-dump``
(each is a preset, so the file is run only when the preset slot is free). b1 (dump off against the
.7a tip: 0 changed, 0 removed, 0 added) needs a run of that older commit and is done by hand with
``tools/leafdiff.py``; it is in the unit Log.

* b2: ``results.json`` of the two runs is bitwise equal (floats by IEEE bytes) except that the
  dump run's ``provenance`` block has the extra leaf ``states_dump`` (and its own command line).
  Reference: ``tools/leafdiff.py``'s comparison, which excludes ``provenance`` and ``seconds``,
  and the provenance blocks compared here by hand.
* b3: the production summary function applied to each dumped array reproduces its results leaf:
  V4 median and mean absolute deviation, the Q-N Delta R^2 (``analysis.delta_r2``), the H1b PLP
  slope (``statistics.ols_slope``), the median weight profile and the H2b median weights, the
  per-rule MSE at ``H_ref`` and the cell's Levenberg-Marquardt block (``pipeline.lm_block``).
  Bitwise where the function and the order of operations are the same (V4, Q-N, H1b, weight
  profile, H2b, LM); the per-rule MSE leaf is the mean over all (state, draw) pairs while the dump
  holds per-state means, so it is compared to ``2 n E 2**-52`` relative (the worst-case relative
  error of a sum of ``n E`` positive terms is ``gamma_{nE}``, about ``n E 2**-53``, and the two
  orders of summation can differ by twice that).
* b3 also: the clip and replacement counts. The core cell's record pools the three splits, so the
  per-split ``handling/<split>/`` arrays are summed and compared exactly with
  ``handling/cells/<core>/by_kind/<oracle|eval>/counts`` (the eight ``handled`` columns and the
  three clipped-entry totals).
* b4: ``(m_A + m_B) / 2 = m`` for ``E_C``, ``E_P`` and ``C`` at every evaluation horizon of the core
  cell and at ``H_ref`` of every sweep cell, to ``1e-13`` times the exact mean absolute term: the
  moment itself for the two squares (their terms are positive) and the dumped ``abs_C`` (the mean
  of ``|e_C e_P|`` over the draws) for the cross moment. This is the plan's scale.
* b5: the median of the per-state V4 half-widths at ``H_ref`` equals the V4 leaf, bitwise.
* b7: the file size is printed (the Log records it).
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

_SPEC = importlib.util.spec_from_file_location("leafdiff", REPO_ROOT / "tools" / "leafdiff.py")
assert _SPEC is not None and _SPEC.loader is not None
leafdiff = importlib.util.module_from_spec(_SPEC)
sys.modules["leafdiff"] = leafdiff
_SPEC.loader.exec_module(leafdiff)


def run_smoke(out: Path, *flags: str) -> Path:
    env = {**os.environ, "JAX_PLATFORMS": "cpu", "XLA_PYTHON_CLIENT_PREALLOCATE": "false"}
    done = subprocess.run([sys.executable, "-m", "lpcstudy", "--preset", "smoke", "--out", str(out),
                           *flags], cwd=REPO_ROOT, env=env, capture_output=True,
                          timeout=TIMEOUT_SECONDS)
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-15:])
    assert done.returncode == 0, f"smoke {flags} exited {done.returncode}:\n{tail}"
    return out / "smoke"


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    base = tmp_path_factory.mktemp("states_dump")
    off = run_smoke(base / "off")
    on = run_smoke(base / "on", "--states-dump")
    results = {name: json.loads((path / "results.json").read_text())
               for name, path in (("off", off), ("on", on))}
    with np.load(on / "states" / f"{SYSTEM}.npz", allow_pickle=False) as loaded:
        arrays = {key: loaded[key] for key in loaded.files}
    return {"off": off, "on": on, "results": results, "arrays": arrays}


def test_b2_dump_on_equals_dump_off_except_the_provenance_leaf(runs) -> None:
    """b2: no leaf differs, is added or is removed; only the provenance block has the flag's leaf."""
    off, on = runs["results"]["off"], runs["results"]["on"]
    outcome = leafdiff.compare(leafdiff.flatten(off), leafdiff.flatten(on))
    assert outcome["different"] == [] and outcome["added"] == [] and outcome["removed"] == []
    assert len(outcome["common"]) > 1000
    assert "states_dump" not in off["provenance"] and on["provenance"]["states_dump"] is True
    drop = ("states_dump", "argv", "start_utc", "end_utc", "wall_seconds", "peak_rss_bytes",
            "device_peak_bytes")
    assert {k: v for k, v in on["provenance"].items() if k not in drop} == \
        {k: v for k, v in off["provenance"].items() if k not in drop}
    assert not (runs["off"] / "states").exists()
    assert (runs["on"] / "states" / f"{SYSTEM}.npz").is_file()


def test_b3_the_production_summaries_of_the_dumped_arrays_reproduce_their_leaves(runs) -> None:
    """b3: V4, Q-N, H1b, weight profile, H2b and LM leaves from the dump; per-rule MSE to gamma_nE."""
    from lpcstudy import analysis as an
    from lpcstudy.config import SMOKE
    from lpcstudy.pipeline import lm_block
    from lpcstudy.statistics import ols_slope

    a, res = runs["arrays"], runs["results"]["on"]["systems"][SYSTEM]
    ref_index = int(a["core/ref_index"])
    # V4 and b5
    for mi, m in enumerate(a["v4/M"].tolist()):
        leaf = res["validation"]["convergence"][str(m)]
        assert float(np.median(a["v4/half_width"][mi, :, 0])) == leaf["median_half_width"]
        assert float(np.mean(np.abs(a["v4/signed_dev"][mi, :, 0]))) == leaf["mean_abs_dev_from_max"]
    assert bool(a["v4/extra_href_equal"]) is True
    # Q-N
    for kind in ("oracle", "deployable"):
        for target in ("logit_w_interior", "w_zero_indicator", "log_horizon"):
            key = f"qn/{kind}/{target}"
            rows = np.flatnonzero(a[f"{key}/domain"])
            got = an.delta_r2(a[f"{key}/y"], a[f"{key}/pred3"], a[f"{key}/pred4"], rows)
            assert got == res["Q-N"][kind][target]["delta_r2"], key
    # H1b PLP slope: x = log(g_H delta / sqrt(m)), y = 0.5 log(max(E_P, 1e-12)), finite pairs
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
    # per-rule MSE at H_ref: the mean of the per-state means, to 2 n E 2**-52 relative
    n_states, n_draws = a["core/state_mse/A0"].shape[0], a["core/R"].shape[1]
    for rule, score in res["scores"].items():
        mean_state = float(np.mean(a[f"core/state_mse/{rule}"][:, ref_index]))
        assert mean_state == pytest.approx(score["mse_href"], rel=2 * n_states * n_draws * 2.0**-52,
                                           abs=0.0), rule
    # the clip and replacement counts: the cell record pools the three splits
    from lpcstudy.ensemble import DRAW_COUNTERS, ENTRY_COUNTERS
    cell = runs["results"]["on"]["systems"][SYSTEM]["handling"]["cells"][CORE_CELL]
    for kind in ("oracle", "eval"):
        counts = cell["by_kind"][kind]["counts"]
        for column, name in enumerate(DRAW_COUNTERS):
            assert sum(int(a[f"handling/{sp}/{kind}_handled"][:, column].sum())
                       for sp in ("construction", "calibration", "test")) == counts[name], \
                (kind, name)
        for column, name in enumerate(ENTRY_COUNTERS):
            assert sum(int(a[f"handling/{sp}/{kind}_clip_entries"][column])
                       for sp in ("construction", "calibration", "test")) == counts[name], \
                (kind, name)
    # the cell's Levenberg-Marquardt block, pooled over the three splits in the run's order
    parts = {kind: [tuple(a[f"lm/{split}/{kind}_{name}"] for name in ("residual", "accepted", "late"))
                    for split in ("construction", "calibration", "test")]
             for kind in ("oracle", "eval")}
    block = lm_block(parts, SMOKE.core_noise, SMOKE.embedding_dim - 3)
    stored = runs["results"]["on"]["systems"][SYSTEM]["handling"]["cells"][CORE_CELL]["lm"]
    assert json.dumps(block, sort_keys=True) == json.dumps(stored, sort_keys=True)


def test_b4_the_two_halves_average_to_the_full_moment(runs) -> None:
    """b4: ``(m_A + m_B) / 2 = m`` to 1e-13 times the exact mean absolute term, core and sweep cells."""
    a = runs["arrays"]
    assert a["core/half_n_draws"].tolist() == [15, 15]
    groups = [("core/", None)] + [(f"{k.rsplit('/', 1)[0]}/", None) for k in a
                                  if k.startswith("sweep/") and k.endswith("/w_star_href")]
    assert len(groups) >= 4  # the core and at least the three sweep cells of the smoke preset
    for prefix, _ in groups:
        assert a[f"{prefix}half_n_draws"].tolist() == [15, 15]
        scale = {"E_C": a[f"{prefix}E_C"], "E_P": a[f"{prefix}E_P"], "C": a[f"{prefix}abs_C"]}
        for name, bound in scale.items():
            mean_half = 0.5 * (a[f"{prefix}{name}_A"] + a[f"{prefix}{name}_B"])
            assert np.all(np.abs(mean_half - a[f"{prefix}{name}"]) <= 1e-13 * bound), (prefix, name)


def test_the_key_tree_has_no_key_that_is_also_a_prefix_and_the_qn_inputs_exist(runs) -> None:
    """R6 and R10: no dumped key is the ``/`` prefix of another, and ``qn/<kind>/`` has its inputs.

    Reference: the schema in ``lpcstudy/dump.py`` (names typed here). Exact.
    """
    keys = set(runs["arrays"])
    assert not any(other.startswith(key + "/") for key in keys for other in keys)
    for kind in ("oracle", "deployable"):
        for name in ("x_test", "w_star", "log_t"):
            assert f"qn/{kind}/{name}" in keys, (kind, name)
        for target in ("logit_w_interior", "w_zero_indicator", "log_horizon"):
            for name in ("pred3", "pred4", "y", "domain"):
                assert f"qn/{kind}/{target}/{name}" in keys, (kind, target, name)


def test_b7_the_dump_size_is_reported(runs) -> None:
    """b7: the size at smoke (recorded in the unit Log; the pilot and full sizes are estimated there)."""
    path = runs["on"] / "states" / f"{SYSTEM}.npz"
    print(f"states dump size at smoke: {path.stat().st_size} bytes, {len(runs['arrays'])} arrays")
    assert 0 < path.stat().st_size < 5_000_000
