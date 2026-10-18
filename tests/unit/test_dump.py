"""Tests for ``lpcstudy.dump``, the opt-in dump of per-state arrays.

The dump (WU-0003.7b; plan B1 item 8, B2 row .7b) writes, for each system, a
file of arrays that the rehearsal diagnostics read. It must only copy or
rearrange numbers the run already computed, never change them.

References (none is the output of the code under test): small hand-built
"worlds" whose every dumped array is decided by hand or by a formula written in
the test. The formulas are the oracle weight ``(E_P - C) / (E_C + E_P - 2 C)``
clipped to [0, 1], the squared error of a blend, and the leaf of a stump (a
decision tree with one split) at 0.5. The other references are the arrays the
test itself put in, and ``np.load`` of the file that was written.

Tolerance: none. A dump array is a copy or a pure elementwise function of a
stored array, so equality is exact, except where a test says otherwise and
justifies it.
"""

from __future__ import annotations

import dataclasses
import hashlib
import struct
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from sklearn.tree import DecisionTreeRegressor

from lpcstudy import dump as dump_module
from lpcstudy.allocation import ProfileProxies, RegimeMap, SeedProxy
from lpcstudy.config import SMOKE
from lpcstudy.dump import SCHEMA, StateDump, clean
from lpcstudy.ensemble import DRAW_COUNTERS, EvaluationDraws
from lpcstudy.oracle import StateOracles
from unit_helpers import moments_from_triples

N, E, M, N_CAL, N_SWEEP = 4, 2, 6, 3, 3
CFG = dataclasses.replace(
    SMOKE,
    horizon_max_lyapunov=4.0,
    n_oracle_draws=M,
    n_eval_draws=E,
    n_test=N,
    n_test_sweep=N_SWEEP,
)
HORIZONS = np.array(CFG.eval_horizons)  # 8, 15, 30, 60, 120
COLS = HORIZONS - 1
REF = CFG.reference_horizon  # 30
RULES = ("A0", "A1", "A2", "A3", "A4", "A5", "A4o", "A*")


def test_clean_copies_and_refuses_what_is_not_float64_int_bool_or_str() -> None:
    """``clean`` returns an independent copy and refuses unsupported types.

    Allowed types are float64, int64, bool and str.

    Reference: the contract in its docstring (PRIME.4: nothing is converted
    silently). A float64 array is copied (writing to the copy leaves the
    source), an int32 array becomes int64 with the same values, a bool and a
    str stay; float32, an object array (``None``), complex and unsigned
    integers raise ``TypeError`` naming the key.

    Tolerance: exact.
    """
    source = np.array([1.5, 2.5])
    copy = clean("a", source)
    copy[0] = -1.0
    assert (
        source[0] == 1.5
        and copy.dtype == np.float64
        and not np.shares_memory(copy, source)
    )
    wide = clean("b", np.array([1, -2], dtype=np.int32))
    assert wide.dtype == np.int64 and wide.tolist() == [1, -2]
    assert clean("c", np.array([True, False])).dtype == bool
    assert clean("d", "abc").dtype.kind == "U"
    for bad in (
        np.array([1.0], dtype=np.float32),
        np.array(None),
        np.array([1j]),
        np.array([1], dtype=np.uint8),
    ):
        with pytest.raises(TypeError, match="dump array 'bad'"):
            clean("bad", bad)


def _stump_map(split: float = 0.5) -> RegimeMap:
    """Return a 2-leaf tree on profile coordinate 2, split at ``split``.

    Coordinate 2 is ``Lambda_hat / lambda_max``. The tree is fitted on the two
    points 0 and ``2 * split`` (so the one split is their midpoint). The map
    under K = 3 of ``_world`` is a decoy with another split (0.1): a dump that
    read the wrong fitted K would give other leaves.
    """
    fit = np.zeros((2, 4))
    fit[:, 2] = [0.0, 2.0 * split]
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0).fit(
        fit, [0.0, 1.0]
    )
    assert tree.tree_.feature[0] == 2
    assert tree.tree_.threshold[0] == pytest.approx(split)
    return RegimeMap(
        tree=tree,
        leaf_ids=np.nonzero(tree.tree_.children_left == -1)[0],
        weights=np.zeros((2, 1)),
        horizons_km=np.full(2, np.nan),
    )


def _draws(
    rng: np.random.Generator, n: int, growth: np.ndarray, n_hor: int
) -> EvaluationDraws:
    """Return random evaluation draws for ``n`` states with given growth."""
    return EvaluationDraws(
        horizons=np.arange(1, n_hor + 1),
        cp_err=rng.standard_normal((n, E, n_hor)),
        plp_err=rng.standard_normal((n, E, n_hor)),
        verify_noise=np.zeros((n, E, n_hor)),
        distance=0.01 + rng.random((n, E)),
        est_nu=1.0 + rng.random((n, E)),
        growth_proxy=growth,
        gain_proxy=np.ones((n, E, n_hor)),
        inputs=np.zeros((n, E, 1)),
        noise_sens=rng.random((n, E)),
        handled=rng.integers(0, 3, (n, 8)).astype(np.int64),
        lm_residual=rng.random((n, E)),
        lm_accepted=rng.integers(0, 15, (n, E)),
        lm_late=rng.integers(0, 2, (n, E)).astype(bool),
    )


def _moments(
    rng: np.random.Generator, n: int, n_hor: int, horizons: np.ndarray
):
    """Return random, valid oracle moments for ``n`` states."""
    e_c = 1.0 + rng.random((n, n_hor))
    e_p = 1.0 + rng.random((n, n_hor))
    cross = 0.5 * np.minimum(e_c, e_p) * (2.0 * rng.random((n, n_hor)) - 1.0)
    m = moments_from_triples(e_c, e_p, cross)
    return dataclasses.replace(
        m,
        horizons=horizons,
        analog_seed=0.1 + rng.random(n),
        est_seed=0.1 + rng.random(n),
        noise_sens=rng.random(n),
        err_corr=2.0 * rng.random((n, n_hor)) - 1.0,
        handled=rng.integers(0, 3, (n, 8)).astype(np.int64),
        lm_residual=rng.random((n, M)),
        lm_accepted=rng.integers(0, 15, (n, M)),
        lm_late=rng.integers(0, 2, (n, M)).astype(bool),
    )


def _halves(
    rng: np.random.Generator, m, n_rows: int, n_hor: int
) -> dict[str, np.ndarray]:
    """Return fake half-draw moments close to the full moments ``m``."""
    out = {}
    for stem in ("sq_cp", "sq_plp", "cross"):
        full = getattr(m, stem)[:n_rows]
        out[f"{stem}_A"] = full * (1.0 + 0.1 * rng.random(full.shape))
        out[f"{stem}_B"] = full * (1.0 - 0.1 * rng.random(full.shape))
    out["abs_cross"] = 0.9 * np.sqrt(m.sq_cp[:n_rows] * m.sq_plp[:n_rows])
    out["n_draws"] = np.array([M // 2, M - M // 2])
    return out


def _world():
    """Return a hand-built system and its dump.

    The system has a core cell, rules, weights, scores, and sweep cells.
    """
    rng = np.random.default_rng(70001)
    n_hor = 120
    m = _moments(rng, N, n_hor, np.arange(1, n_hor + 1))
    # growth * 30 = 0.0, 0.3, 0.6, 1.2
    growth = np.array([[0.0, 0.01], [0.02, 0.04], [0.01, 0.0], [0.04, 0.04]])
    ev = _draws(rng, N, growth, n_hor)
    cal = _draws(
        rng, N_CAL, np.array([[0.0, 0.04], [0.01, 0.02], [0.03, 0.0]]), n_hor
    )
    oracles = StateOracles(
        nu=rng.random(N),
        gains=1.0 + rng.random((N, 30)),
        growth=rng.random(N),
        local_dim=2.0 + rng.random(N),
        handled=rng.integers(0, 2, (N, 3)).astype(np.int64),
    )
    lm = lambda n, k: SimpleNamespace(
        lm_residual=rng.random((n, k)),
        lm_accepted=rng.integers(0, 15, (n, k)),
        lm_late=rng.integers(0, 2, (n, k)).astype(bool),
        handled=rng.integers(0, 3, (n, 8)).astype(np.int64),
        clip_entries={
            "error_clips_cp": int(rng.integers(0, 9)),
            "error_clips_plp": 3,
            "error_clips_nonfinite": int(rng.integers(0, 4)),
        },
    )
    core = SimpleNamespace(
        system="lorenz63",
        noise=0.01,
        library_size=10_000,
        horizons=np.arange(1, n_hor + 1),
        splits={
            "construction": SimpleNamespace(moments=lm(5, M), evals=lm(5, E)),
            "calibration": SimpleNamespace(moments=lm(N_CAL, M), evals=cal),
            "test": SimpleNamespace(moments=m, evals=ev),
        },
        oracles={"test": oracles},
    )
    # the clip entry totals of the real computations (dicts), distinct per part
    m.clip_entries = {
        "error_clips_cp": 1,
        "error_clips_plp": 2,
        "error_clips_nonfinite": 0,
    }
    ev.clip_entries = {
        "error_clips_cp": 4,
        "error_clips_plp": 0,
        "error_clips_nonfinite": 1,
    }
    cal.clip_entries = {
        "error_clips_cp": 7,
        "error_clips_plp": 7,
        "error_clips_nonfinite": 7,
    }
    rules = SimpleNamespace(
        proxies=ProfileProxies(
            SeedProxy(1.0, 2.0, nfev=11, status=2),
            SeedProxy(0.5, 0.25, nfev=5, status=1),
            nu_cap=7.5,
        ),
        regimes={2: _stump_map(), 3: _stump_map(split=0.1)},
        chosen_regimes=2,
    )
    weights = {rule: rng.random((N, E, n_hor)) for rule in RULES}
    scores = {
        rule: SimpleNamespace(
            state_mse_ref=(
                (
                    w[:, :, REF - 1] * ev.cp_err[:, :, REF - 1]
                    + (1 - w[:, :, REF - 1]) * ev.plp_err[:, :, REF - 1]
                )
                ** 2
            ).mean(axis=1)
        )
        for rule, w in weights.items()
    }
    dump = StateDump()
    core_halves = _halves(rng, m, N, n_hor)
    dump.record_halves(
        "lorenz63", 0.01, 10_000, True, core.horizons, core_halves
    )
    # sweep cells: the core view (rho 1%, n_lib 1e4: no record of its own), a
    # noise cell and a library cell, three states, the five evaluation horizons
    sweep = {}
    for key in ((0.02, 10_000), (0.01, 1_000)):
        sm = _moments(rng, N_SWEEP, 5, HORIZONS)
        sweep[key] = SimpleNamespace(
            noise=key[0],
            library_size=key[1],
            splits={"test": SimpleNamespace(moments=sm)},
        )
        dump.record_halves(
            "lorenz63", *key, False, HORIZONS, _halves(rng, sm, N_SWEEP, 5)
        )
    sm = _moments(rng, N_SWEEP, 5, HORIZONS)
    core_view = SimpleNamespace(
        noise=0.01,
        library_size=10_000,
        splits={"test": SimpleNamespace(moments=sm)},
    )
    noise_cells = {0.01: core_view, 0.02: sweep[(0.02, 10_000)]}
    library_cells = {
        (0.01, 10_000): core_view,
        (0.01, 1_000): sweep[(0.01, 1_000)],
    }
    dump.record_v4(
        "lorenz63",
        {
            "M": np.array([2, 4]),
            "horizons": np.array([30, 60, 120]),
            "w_hat": rng.random((2, 5, 3)),
        },
    )
    dump.record_qn("lorenz63", "oracle", {"x_test": rng.random((N, 4))})
    dump.record_extra("lorenz63", EXTRA)
    return (
        dump,
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        core_halves,
        {"core_view": core_view, **{k: v for k, v in sweep.items()}},
    )


# The schema /2 groups, as `run_system` hands them over (WU-0003.7c).
EXTRA = {
    "h1c/thresholds": np.array([0.1, 0.2, 0.3, 0.5]),
    "h1c/PLP/ratio": np.array([1.0, np.nan, 0.9, np.inf]),
    "h1c/PLP/eligible": np.array([True, False, True, True]),
    "h1c/CP/ratio": np.array([1.5, np.nan, np.nan, 1.1]),
    "h1c/CP/eligible": np.array([True, False, False, True]),
    "h1a/noise_levels": np.array([0.01, 0.02]),
    "h1a/n_lib": np.array([1000.0, 10000.0]),
    "h1a/local_dim": np.array([2.0, np.nan, 2.5]),
    "h1a/inverse_dim": np.array([0.4, np.nan, 0.3]),
    "h1a/rho=0.01/seed_sq": np.array([[1.0, 0.5], [2.0, 1.0], [3.0, 1.5]]),
    "h1a/rho=0.02/seed_sq": np.array([[1.5, 0.7], [2.5, 1.2], [3.5, 1.7]]),
}


def oracle_w(e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray) -> np.ndarray:
    """Return the clipped oracle weight from FW Proposition 3.

    It is written here from the formula, not taken from the library.
    """
    return np.clip((e_p - cross) / (e_c + e_p - 2.0 * cross), 0.0, 1.0)


def test_collect_dumps_every_core_array_as_the_hand_formula_says() -> None:
    """``collect`` puts hand-checkable values in the ``core/`` group.

    The schema and the dtypes must be as documented.

    Reference: formulas written in the test. ``E_C``, ``E_P``, ``C`` at the
    five evaluation horizons are the stored moments at columns h - 1.
    ``w_star`` and its halves are ``clip((E_P - C) / (E_C + E_P - 2 C), 0, 1)``
    of them (the weight of Proposition 3, written here). The A5 leaf of every
    (state, draw) is decided by hand from the manufactured stump split at 0.5
    on ``growth * 30`` (the values 0.0, 0.3, 0.6, 1.2 are far from it). The
    per-rule state MSE is ``mean_e ((w e_C + (1 - w) e_P)^2)`` at each
    evaluation horizon. The rule weights at ``H_ref`` are the stored column
    29. The dtypes are float64, int64, bool or str, and ``meta/schema`` is
    ``SCHEMA``.

    Tolerance: exact (elementwise formulas on identical inputs; the mean over
    two draws is a sum of two terms halved, the same operation in both).
    """
    (
        dump,
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        halves,
        _,
    ) = _world()
    arrays = dump.collect(
        "lorenz63",
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        CFG,
    )
    m, ev = core.splits["test"].moments, core.splits["test"].evals
    assert str(arrays["meta/schema"]) == SCHEMA == "lpcstudy.states/2"
    assert (
        arrays["core/horizons"].tolist() == HORIZONS.tolist()
        and int(arrays["core/ref_index"]) == 2
    )
    assert arrays["meta/draw_counters"].tolist() == list(DRAW_COUNTERS)
    for name, stem in (("E_C", "sq_cp"), ("E_P", "sq_plp"), ("C", "cross")):
        assert np.array_equal(arrays[f"core/{name}"], getattr(m, stem)[:, COLS])
        for tag in ("A", "B"):
            assert np.array_equal(
                arrays[f"core/{name}_{tag}"], halves[f"{stem}_{tag}"][:, COLS]
            )
    assert np.array_equal(
        arrays["core/w_star"],
        oracle_w(m.sq_cp[:, COLS], m.sq_plp[:, COLS], m.cross[:, COLS]),
    )
    for tag in ("A", "B"):
        assert np.array_equal(
            arrays[f"core/w_star_{tag}"],
            oracle_w(
                halves[f"sq_cp_{tag}"][:, COLS],
                halves[f"sq_plp_{tag}"][:, COLS],
                halves[f"cross_{tag}"][:, COLS],
            ),
        )
    assert arrays["core/half_n_draws"].tolist() == [3, 3]
    for name, source in (
        ("eps_s", m.analog_seed),
        ("delta", m.est_seed),
        ("N", m.noise_sens),
        ("nu", core.oracles["test"].nu),
        ("Lambda_bar", core.oracles["test"].growth),
        ("d", core.oracles["test"].local_dim),
        ("R", ev.distance),
    ):
        assert np.array_equal(arrays[f"core/{name}"], source), name
        assert not np.shares_memory(arrays[f"core/{name}"], source), name
    assert np.array_equal(
        arrays["core/g_H_ref"], core.oracles["test"].gains[:, REF - 1]
    )
    assert arrays["core/profile"].shape == (N, E, 4)
    # A5 leaves by hand: coordinate 2 is growth * 30 = 0.0, 0.3, 0.6, 1.2 (...),
    # split at 0.5
    hand = lambda g: np.where(g * 30 <= 0.5, 1, 2)
    assert np.array_equal(arrays["core/a5_leaf"], hand(ev.growth_proxy))
    assert np.array_equal(
        arrays["core/a5_leaf_calibration"],
        hand(core.splits["calibration"].evals.growth_proxy),
    )
    assert arrays["core/a5_leaf"].dtype == np.int64
    for rule in ("A2", "A3", "A4", "A5"):
        assert np.array_equal(
            arrays[f"core/weight_href/{rule}"], weights[rule][:, :, REF - 1]
        )
    for rule in RULES:
        w = weights[rule]
        err = (
            w[:, :, COLS] * ev.cp_err[:, :, COLS]
            + (1 - w[:, :, COLS]) * ev.plp_err[:, :, COLS]
        )
        assert np.array_equal(
            arrays[f"core/state_mse/{rule}"], (err**2).mean(axis=1)
        ), rule
    assert np.array_equal(arrays["core/abs_C"], halves["abs_cross"][:, COLS])
    # every split: the LM summaries of the run pool them
    for split, part in core.splits.items():
        for kind, source in (("oracle", part.moments), ("eval", part.evals)):
            for name in ("residual", "accepted", "late"):
                assert np.array_equal(
                    arrays[f"lm/{split}/{kind}_{name}"],
                    getattr(source, f"lm_{name}"),
                ), (split, kind, name)
    names = ["error_clips_cp", "error_clips_plp", "error_clips_nonfinite"]
    assert arrays["meta/clip_entry_names"].tolist() == names
    # b3: the counts of the splits sum to the cell record's counts
    for split, part in core.splits.items():
        for kind, source in (("oracle", part.moments), ("eval", part.evals)):
            assert np.array_equal(
                arrays[f"handling/{split}/{kind}_handled"], source.handled
            )
            assert arrays[f"handling/{split}/{kind}_handled"].dtype == np.int64
            assert arrays[f"handling/{split}/{kind}_clip_entries"].tolist() == [
                source.clip_entries[k] for k in names
            ]
    assert arrays["handling/test/oracle_clip_entries"].tolist() == [1, 2, 0]
    assert arrays["handling/test/eval_clip_entries"].tolist() == [4, 0, 1]
    assert arrays["handling/calibration/eval_clip_entries"].tolist() == [
        7,
        7,
        7,
    ]
    # schema /2: stored as given, with the dtype kept
    for key, value in EXTRA.items():
        assert np.array_equal(
            arrays[key], value, equal_nan=value.dtype.kind == "f"
        ), key
        assert arrays[key].dtype == value.dtype, key
        assert not np.shares_memory(arrays[key], value), key
    assert arrays["lm/test/oracle_late"].dtype == bool
    assert arrays["lm/test/oracle_accepted"].dtype == np.int64
    assert arrays["lm/construction/oracle_residual"].shape == (5, M)
    for key, value in arrays.items():
        assert value.dtype.kind in "fibU" and (
            value.dtype.kind != "f" or value.dtype.itemsize == 8
        ), key


def test_collect_dumps_the_sweep_cells_with_the_core_view_taken_from_the_core_halves() -> (
    None
):
    """``sweep/rho=<g>|n_lib=<n>/`` holds ``w*(H_ref)`` and the moments.

    It also holds the error correlation and the half-draw moments at ``H_ref``.

    Reference: formulas written in the test. There are three distinct cells
    (the core view, the 2% noise cell, the 1e3 library cell; the core view
    appears in both dicts and once in the file). The core view has no record
    of its own, so its half moments are the first three states of the core
    cell at column ``H_ref - 1``; the other two use their own records at the
    ``H_ref`` position of the evaluation horizons (index 2). ``w*`` is the
    weight formula of Proposition 3 on the sweep moments at ``H_ref``;
    ``err_corr_href`` is the stored column.

    Tolerance: exact.
    """
    (
        dump,
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        halves,
        cells,
    ) = _world()
    records = dict(dump._halves)  # collect drops the records of the system
    arrays = dump.collect(
        "lorenz63",
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        CFG,
    )
    groups = sorted(
        {k.rsplit("/", 1)[0] for k in arrays if k.startswith("sweep/")}
    )
    assert groups == [
        "sweep/rho=0.01|n_lib=1000",
        "sweep/rho=0.01|n_lib=10000",
        "sweep/rho=0.02|n_lib=10000",
    ]
    own = {
        (0.02, 10_000): cells[(0.02, 10_000)],
        (0.01, 1_000): cells[(0.01, 1_000)],
        (0.01, 10_000): cells["core_view"],
    }
    for (rho, n_lib), cell in own.items():
        sm = cell.splits["test"].moments
        group = f"sweep/rho={rho:g}|n_lib={n_lib}"
        assert np.array_equal(
            arrays[f"{group}/w_star_href"],
            oracle_w(sm.sq_cp[:, 2], sm.sq_plp[:, 2], sm.cross[:, 2]),
        )
        assert np.array_equal(
            arrays[f"{group}/err_corr_href"], sm.err_corr[:, 2]
        )
        for name, stem in (("E_C", "sq_cp"), ("E_P", "sq_plp"), ("C", "cross")):
            assert np.array_equal(
                arrays[f"{group}/{name}"], getattr(sm, stem)[:, 2]
            ), name
        assert arrays[f"{group}/half_n_draws"].tolist() == [3, 3]
    # own records: abs_C at the H_ref position
    for key in (("0.02", 10_000), ("0.01", 1_000)):
        record = records[("lorenz63", float(key[0]), key[1], False)]
        assert np.array_equal(
            arrays[f"sweep/rho={key[0]}|n_lib={key[1]}/abs_C"],
            record["abs_cross"][:, 2],
        )
    core_group = "sweep/rho=0.01|n_lib=10000"
    assert np.array_equal(
        arrays[f"{core_group}/abs_C"], halves["abs_cross"][:N_SWEEP, REF - 1]
    )
    for name, stem in (("E_C", "sq_cp"), ("E_P", "sq_plp"), ("C", "cross")):
        for tag in ("A", "B"):
            assert np.array_equal(
                arrays[f"{core_group}/{name}_{tag}"],
                halves[f"{stem}_{tag}"][:N_SWEEP, REF - 1],
            )


def test_collect_and_write_round_trip_and_the_schema_is_documented(
    tmp_path: Path,
) -> None:
    """The file reads back bitwise; every key is documented.

    Pending records are dropped.

    Reference: ``np.load`` of the written file (``allow_pickle`` false, so no
    object array can hide), the arrays the test put into the V4 and Q-N
    records, and the module docstring as the schema text: each key component
    (except a cell group, a rule label and a target name) must appear in it.
    After ``collect`` the half-draw, V4 and Q-N records of the system are gone,
    so a second ``collect`` raises ``KeyError`` (one file per system, never
    two).

    Tolerance: exact.
    """
    dump, core, rules, weights, scores, noise_cells, library_cells, _, _ = (
        _world()
    )
    arrays = dump.collect(
        "lorenz63",
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        CFG,
    )
    path = tmp_path / "states" / "lorenz63.npz"
    size = StateDump.write(path, arrays)
    assert size == path.stat().st_size > 0
    with np.load(path, allow_pickle=False) as loaded:
        assert sorted(loaded.files) == sorted(arrays)
        for key in arrays:
            # bitwise: NaN arrays too
            assert (
                loaded[key].dtype == arrays[key].dtype
                and loaded[key].shape == arrays[key].shape
                and loaded[key].tobytes() == arrays[key].tobytes()
            ), key
    assert arrays["v4/w_hat"].shape == (2, 5, 3)
    assert arrays["qn/oracle/x_test"].shape == (N, 4)
    # R10: no key is also the "/" prefix of another (a tree built from the keys
    # must not collide)
    assert not any(
        other.startswith(key + "/") for key in arrays for other in arrays
    )
    skip = set(weights) | {"qn", "sweep", "construction", "calibration", "test"}
    text = dump_module.__doc__
    for key in arrays:
        for part in key.split("/"):
            if part.startswith("rho=") or part in skip:
                continue
            assert part in text, (key, part)
    with pytest.raises(KeyError):
        dump.collect(
            "lorenz63",
            core,
            rules,
            weights,
            scores,
            noise_cells,
            library_cells,
            CFG,
        )


def test_collect_refuses_a_missing_half_record_and_a_state_mse_that_disagrees() -> (
    None
):
    """A missing half-draw record raises ``KeyError``; a wrong state MSE raises.

    Reference: the contract (a dump never writes a partial or inconsistent
    file, PRIME.4). The first case is a sweep cell with no record anywhere;
    the second perturbs one score at ``H_ref`` by one ulp (the smallest float
    step), which the bitwise cross-check against ``RuleScores.state_mse_ref``
    must catch.

    Tolerance: exact.
    """
    dump, core, rules, weights, scores, noise_cells, library_cells, _, cells = (
        _world()
    )
    stray = SimpleNamespace(
        noise=0.05, library_size=10_000, splits=cells["core_view"].splits
    )
    with pytest.raises(KeyError, match="no half-draw moments"):
        dump.collect(
            "lorenz63",
            core,
            rules,
            weights,
            scores,
            {**noise_cells, 0.05: stray},
            library_cells,
            CFG,
        )
    dump, core, rules, weights, scores, noise_cells, library_cells, _, _ = (
        _world()
    )
    scores["A4"].state_mse_ref[1] = np.nextafter(
        scores["A4"].state_mse_ref[1], 10.0
    )
    with pytest.raises(ValueError, match="state_mse of A4"):
        dump.collect(
            "lorenz63",
            core,
            rules,
            weights,
            scores,
            noise_cells,
            library_cells,
            CFG,
        )


def test_the_a5_leaf_arrays_digest_to_the_fitted_leaf() -> None:
    """The dumped A5 leaf arrays hash to the fitted digest.

    The arrays are ``a5_leaf_calibration`` then ``a5_leaf``.

    The digest is the leaf ``fitted/a5_leaf_digest``.

    Reference: ``hashlib.sha256`` of the int64 values of the two arrays packed
    with ``struct``, calibration first, C order (the definition of the .7a
    leaf), compared with ``experiments.fitted_record`` on the same hand-built
    world.

    Tolerance: exact.
    """
    from lpcstudy.experiments import fitted_record

    dump, core, rules, weights, scores, noise_cells, library_cells, _, _ = (
        _world()
    )
    rules.predictor = SimpleNamespace(
        network=SimpleNamespace(weights_digest=lambda: "0" * 64)
    )
    for rule in rules.regimes.values():
        rule.weights = np.zeros((2, CFG.reference_horizon))
    arrays = dump.collect(
        "lorenz63",
        core,
        rules,
        weights,
        scores,
        noise_cells,
        library_cells,
        CFG,
    )
    values = [
        int(v)
        for part in ("a5_leaf_calibration", "a5_leaf")
        for v in arrays[f"core/{part}"].ravel()
    ]
    reference = hashlib.sha256(
        struct.pack("<%dq" % len(values), *values)
    ).hexdigest()
    assert fitted_record(core, rules, CFG)["a5_leaf_digest"] == reference


def test_the_a5_leaf_arrays_follow_the_chosen_k_not_another_fitted_k() -> None:
    """The A5 leaf arrays are the leaves of the map under ``chosen_regimes``.

    This covers ``core/a5_leaf`` and ``core/a5_leaf_calibration``.

    Reference: the manufactured stumps decided by hand (``_world`` holds K = 2
    split at 0.5 and a decoy K = 3 split at 0.1, on ``growth * 30``; the
    values 0.0, 0.3, 0.6, 0.9, 1.2 are on the two sides of the split of the
    decoy but not of the other: 0.3 and 0.6 and 0.9 give leaf 2 under 0.1 and
    0.3 gives leaf 1 under 0.5). With K = 2 chosen the leaves are the 0.5 ones
    (and differ from those of the decoy); with K = 3 chosen they are the 0.1
    ones. A dump that read the first, the largest or a fixed K would fail one
    of the two.

    Tolerance: exact.
    """
    hand = lambda g, split: np.where(g * 30 <= split, 1, 2)
    for chosen, split, other in ((2, 0.5, 0.1), (3, 0.1, 0.5)):
        dump, core, rules, weights, scores, noise_cells, library_cells, _, _ = (
            _world()
        )
        rules.chosen_regimes = chosen
        arrays = dump.collect(
            "lorenz63",
            core,
            rules,
            weights,
            scores,
            noise_cells,
            library_cells,
            CFG,
        )
        test_growth = core.splits["test"].evals.growth_proxy
        cal_growth = core.splits["calibration"].evals.growth_proxy
        assert np.array_equal(arrays["core/a5_leaf"], hand(test_growth, split))
        assert np.array_equal(
            arrays["core/a5_leaf_calibration"], hand(cal_growth, split)
        )
        assert not np.array_equal(
            arrays["core/a5_leaf_calibration"], hand(cal_growth, other)
        )


def test_record_extra_refuses_keys_outside_h1a_h1c_and_a_key_recorded_twice() -> (
    None
):
    """``record_extra`` takes only ``h1a/`` and ``h1c/`` keys, once each (R2).

    A refusal records nothing.

    Reference: the contract (a key of schema /1 is never silently replaced,
    PRIME.4), decided by hand. A ``core/`` key, a ``meta/`` key, a ``qn/`` key
    and a bare name are refused with ``ValueError`` naming the key. An
    ``h1c/`` key given twice, in one call or two, is refused. A call that
    mixes a good key and a bad one records neither (so the system has no
    pending record and ``collect`` still raises ``KeyError`` for the missing
    extras, not a half-filled dict).

    Tolerance: exact.
    """
    dump = StateDump()
    for bad in ("core/E_C", "meta/schema", "qn/oracle/x_test", "h1c", "h1a"):
        with pytest.raises(ValueError, match="record_extra takes keys"):
            dump.record_extra("lorenz63", {bad: np.zeros(2)})
    with pytest.raises(ValueError, match="record_extra takes keys"):
        dump.record_extra(
            "lorenz63",
            {"h1c/thresholds": np.zeros(2), "core/w_star": np.zeros(2)},
        )
    assert "lorenz63" not in dump._extra
    dump.record_extra("lorenz63", {"h1c/thresholds": np.array([0.1, 0.2])})
    with pytest.raises(ValueError, match="already recorded"):
        dump.record_extra("lorenz63", {"h1c/thresholds": np.array([9.0])})
    with pytest.raises(ValueError, match="already recorded"):
        dump.record_extra(
            "lorenz63",
            {"h1a/n_lib": np.zeros(1), "h1c/thresholds": np.zeros(1)},
        )
    assert list(dump._extra["lorenz63"]) == ["h1c/thresholds"]
    assert dump._extra["lorenz63"]["h1c/thresholds"].tolist() == [0.1, 0.2]
    # another system: its own record
    dump.record_extra("rossler", {"h1c/thresholds": np.zeros(1)})
