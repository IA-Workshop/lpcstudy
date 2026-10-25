"""Tests of the extension systems S1, S2, S3 and of the frozen pins (WU-0021).

Authority: DEC-0037; the unit file ``docs/agent/records/work/WU-0021-extension-
attractors.md`` (acceptance criteria R3 and A1 to A5) and the specification note
``docs/agent/notes/2026-10-20-math-extension-specs.md`` (section 0 for the
values). The extension systems are exploratory: they are outside
``statistics.V3_SYSTEMS`` and every preset.

What is checked, with the independent reference of each check:

* R3 (pins). The three frozen specs, the presets and ``V3_SYSTEMS`` equal
  literals typed here from ``git show freeze-1:lpcstudy/systems.py``,
  ``config.py`` and ``statistics.py``; exact equality.
* A1 (field). Each new field against a NumPy evaluation of the equations as
  quoted in the researcher's notes, at five fixed dyadic states.
* A2 (Jacobian). ``jax.jacfwd`` of each field against the analytic Jacobian
  written by hand in this file.
* A3 (RK4 order). Richardson self-convergence of ``make_flow_step``.
* A4 (V6). The v3 section 6 criterion at the chosen ``max_dt``.
* A5 (guard). ``guard_orbit`` at the bound, just above it and at NaN.
* The S2 bound 185 against the analytic trapping ball.

The slow-tier checks (cached exponents, independent Benettin) are in
``tests/slow/test_extension_lyapunov.py``.
"""

from __future__ import annotations

import dataclasses
import math

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy import systems
from lpcstudy.config import FULL, PILOT, SMOKE
from lpcstudy.statistics import V3_SYSTEMS
from lpcstudy.systems import (
    SYSTEMS,
    OrbitDivergence,
    checked_bound,
    guard_orbit,
    make_flow_step,
)

EPS = 2.0**-52
"""Machine epsilon of float64 (round-off unit of the bounds below)."""

FROZEN = ("lorenz63", "rossler", "chua")
EXTENSION = (
    "rossler_hyper",
    "lorenz63_r166",
    "rossler_z",
    "hindmarsh_rose",
    "hyper_jha",
    "lorenz96_4",
)

# Cached largest Lyapunov exponents of the specification note section 0 (used
# only to set the observation interval 1 / (30 lambda) of the checks below).
LAMBDA = {
    "rossler_hyper": 0.11220508610149857,
    "lorenz63_r166": 0.6217010154674514,
    "rossler_z": 0.07133265490530956,
    "hindmarsh_rose": 0.21688316515721046,
    "hyper_jha": 0.3603046265219353,
    "lorenz96_4": 1.2018430962199733,
}
# Standard deviation of the observed coordinate, specification note section 1
# (S1 21.58, S2 20.34, S3 2.850). A relative error of 10% changes nothing: the
# V6 margin is at least 12 (note section 2).
SIGMA_X = {
    "rossler_hyper": 21.58,
    "lorenz63_r166": 20.34,
    "rossler_z": 2.850,
    "hindmarsh_rose": 0.3057,
    "hyper_jha": 9.656,
    "lorenz96_4": 6.961,
}
# (S4 0.3057, S5 9.656, S6 6.961, specification note 2 section 1; the V6 margins
# are 48, 26 and 180, so a 10% error changes nothing.)


# ------------------------------------------------------------------ R3 pins


def test_frozen_specs_equal_the_freeze_1_literals() -> None:
    """R3: the three frozen specs are unchanged, field by field.

    Reference: the literals below, copied from ``git show freeze-1:
    lpcstudy/systems.py`` (the ratified registry, DEC-0017 Q1 and DEC-0026
    item 3), plus ``lyapunov_steps = 100_000``, the literal that
    ``data.lyapunov_record`` used before the field existed, and
    ``estimator_starts = ("network",)``, the single network start of the
    frozen estimator (WU-0039).

    Tolerance: none; exact equality of floats, tuples and dicts, and identity
    of the field functions.
    """
    expected = {
        "lorenz63": dict(
            params={"sigma": 10.0, "rho": 28.0, "beta": 8.0 / 3.0},
            dim=3,
            observed_index=0,
            initial_state=(1.0, 1.0, 1.0),
            max_dt=0.01,
            orbit_bound=40.0,
            lyapunov_steps=100_000,
            estimator_starts=("network",),
            field_fn=systems.lorenz63_field,
        ),
        "rossler": dict(
            params={"a": 0.2, "b": 0.2, "c": 5.7},
            dim=3,
            observed_index=0,
            initial_state=(1.0, 1.0, 0.0),
            max_dt=0.04,
            orbit_bound=25.0,
            lyapunov_steps=100_000,
            estimator_starts=("network",),
            field_fn=systems.rossler_field,
        ),
        "chua": dict(
            params={"alpha": 15.6, "beta": 28.0, "m0": -1.143, "m1": -0.714},
            dim=3,
            observed_index=0,
            initial_state=(0.7, 0.0, 0.0),
            max_dt=0.005,
            orbit_bound=3.0,
            lyapunov_steps=100_000,
            estimator_starts=("network",),
            field_fn=systems.chua_field,
        ),
    }
    for name, fields in expected.items():
        spec = SYSTEMS[name]
        assert spec.name == name
        for key, value in fields.items():
            if key == "field_fn":
                assert spec.field_fn is value, (name, key)
            else:
                assert getattr(spec, key) == value, (name, key)
                assert type(getattr(spec, key)) is type(value), (name, key)
    # Every field of the dataclass is pinned: a new field must be added here.
    assert {f.name for f in dataclasses.fields(systems.SystemSpec)} == (
        set(expected["chua"]) | {"name"}
    )


def test_presets_and_v3_systems_are_unchanged() -> None:
    """R3: the presets' ``core_systems`` and ``V3_SYSTEMS`` equal the literals.

    Reference: ``config.py`` and ``statistics.py`` at freeze-1, typed here
    (FULL and PILOT run the three systems, SMOKE runs Lorenz-63 only).
    Tolerance: none; exact equality of tuples.
    """
    three = ("lorenz63", "rossler", "chua")
    assert FULL.core_systems == three
    assert PILOT.core_systems == three
    assert SMOKE.core_systems == ("lorenz63",)
    assert V3_SYSTEMS == three


def test_registry_is_frozen_three_plus_the_extension_entries() -> None:
    """The registry holds the frozen three and, separately, the extension three.

    Reference: DEC-0037 and the specification note section 0, written out here.
    No extension system is in a preset or in ``V3_SYSTEMS``. Tolerance: none.
    """
    assert set(SYSTEMS) == set(FROZEN) | set(EXTENSION)
    for name in EXTENSION:
        assert name not in FULL.core_systems
        assert name not in V3_SYSTEMS


def test_extension_specs_equal_the_specification_values() -> None:
    """The extension specs equal specification note section 0, field by field.

    Reference: the table of section 0, typed here (not read from the code).
    ``estimator_starts`` is fix F1 of the V7 diagnosis (note 2026-10-25,
    section 6) on S2, S4, S5 and S6 only, typed here (WU-0039). Tolerance:
    none; exact equality.
    """
    expected = {
        "rossler_hyper": dict(
            params={"a": 0.25, "b": 3.0, "c": 0.5, "d": 0.05},
            dim=4,
            observed_index=0,
            initial_state=(-10.0, -6.0, 0.0, 10.0),
            max_dt=0.005,
            orbit_bound=460.0,
            lyapunov_steps=2_000_000,
            estimator_starts=("network",),
        ),
        "lorenz63_r166": dict(
            params={"sigma": 10.0, "rho": 166.1, "beta": 8.0 / 3.0},
            dim=3,
            observed_index=0,
            initial_state=(1.0, 1.0, 1.0),
            max_dt=0.002,
            orbit_bound=185.0,
            lyapunov_steps=4_000_000,
            estimator_starts=("network", "pair"),
        ),
        "rossler_z": dict(
            params={"a": 0.2, "b": 0.2, "c": 5.7},
            dim=3,
            observed_index=0,
            initial_state=(0.0, 1.0, 1.0),
            max_dt=0.04,
            orbit_bound=50.0,
            lyapunov_steps=1_000_000,
            estimator_starts=("network",),
        ),
        # Specification note 2, section 0 (S4 to S6).
        "hindmarsh_rose": dict(
            params={
                "a": 0.49,
                "b": 1.0,
                "c": 0.0322,
                "d": 1.0,
                "s": 1.0,
                "tx": 0.03,
                "tz": 0.8,
            },
            dim=3,
            observed_index=0,
            initial_state=(0.1, 0.1, 0.1),
            max_dt=0.0025,
            orbit_bound=5.0,
            lyapunov_steps=2_000_000,
            estimator_starts=("network", "pair"),
        ),
        "hyper_jha": dict(
            params={"a": 10.0, "b": 28.0, "c": 2.667, "d": 1.3},
            dim=4,
            observed_index=0,
            initial_state=(1.0, 1.0, 1.0, 1.0),
            max_dt=0.0025,
            orbit_bound=80.0,
            lyapunov_steps=2_000_000,
            estimator_starts=("network", "pair"),
        ),
        "lorenz96_4": dict(
            params={"F": 20.0},
            dim=4,
            observed_index=0,
            initial_state=(20.0, 20.01, 20.0, 20.0),
            max_dt=0.005,
            orbit_bound=60.0,
            lyapunov_steps=1_000_000,
            estimator_starts=("network", "pair"),
        ),
    }
    for name, fields in expected.items():
        spec = SYSTEMS[name]
        assert spec.name == name
        for key, value in fields.items():
            assert getattr(spec, key) == value, (name, key)
    assert set(expected) == set(EXTENSION)
    assert SYSTEMS["lorenz63_r166"].field_fn is systems.lorenz63_field
    assert SYSTEMS["hindmarsh_rose"].field_fn is systems.hindmarsh_rose_field
    assert SYSTEMS["hyper_jha"].field_fn is systems.hyper_jha_field
    assert SYSTEMS["lorenz96_4"].field_fn is systems.lorenz96_ring_field


# ------------------------------------------------- A1 field, A2 Jacobian

# Five dyadic states per system (every coordinate is a multiple of 1/8, so a
# product of two coordinates is exact and the only round-off is in the sums
# and in the products with the non-dyadic parameters).
STATES = {
    "rossler_hyper": [
        (-10.0, -6.0, 0.0, 10.0),
        (0.5, 1.25, -2.0, 0.125),
        (-24.75, 3.5, 12.25, 25.5),
        (60.0, -0.375, 4.0, -7.5),
        (-100.0, 40.0, 0.75, 1.0),
    ],
    "lorenz63_r166": [
        (1.0, 1.0, 1.0),
        (-20.5, 7.25, 150.0),
        (35.0, -40.125, 200.5),
        (0.125, 2.0, 10.0),
        (-55.5, -3.75, 180.25),
    ],
    "rossler_z": [
        (0.0, 1.0, 1.0),
        (0.5, 2.25, -3.0),
        (12.0, -8.5, 6.5),
        (0.0625, 9.0, 4.0),
        (3.0, -5.25, -9.75),
    ],
    "hindmarsh_rose": [
        (0.1015625, 0.0625, 0.125),
        (0.5, -0.25, 0.125),
        (-0.75, 0.375, -0.125),
        (1.5, -0.125, 0.25),
        (-0.0625, 0.5, -0.375),
    ],
    "hyper_jha": [
        (1.0, 1.0, 1.0, 1.0),
        (-12.5, 7.25, 30.0, -60.5),
        (20.0, -15.125, 22.5, 150.0),
        (0.125, 2.0, 10.0, -0.5),
        (-30.5, -3.75, 40.25, 300.0),
    ],
    "lorenz96_4": [
        (20.0, 20.01, 20.0, 20.0),
        (2.5, -3.25, 8.0, 1.5),
        (-10.5, 4.75, 12.0, -6.25),
        (18.0, 0.5, -7.5, 9.0),
        (0.125, 6.0, -14.5, 3.0),
    ],
}

# Round-off bound factor K of A1 and A2: ``|diff| <= K eps sum|terms|``. Each
# evaluation (code and reference) of a component with ``q`` floating-point
# operations on the path of its worst term and ``n`` terms has a relative error
# of at most ``(q + n - 1) eps / 2`` of ``sum|terms|``, and the difference of
# two such evaluations at most ``(q + n - 1) eps``. For the sums of at most
# three terms of two operations (S1 to S3, S5, S6) this is at most 4; for S4
# (``a x^3 / tx`` is four operations, five terms) it is 8.
TOLERANCE_FACTOR = {name: 4.0 for name in EXTENSION}
TOLERANCE_FACTOR["hindmarsh_rose"] = 8.0


def reference_field(name: str, state: np.ndarray, p: dict) -> tuple:
    """Return the NumPy field and the absolute sum of the terms per component.

    The equations are those quoted in the researcher notes. S1 (Rossler 1979,
    researcher note 2026-10-19 request 1; Dysts ``HyperRossler``):
    ``x' = -y - z, y' = x + a y + w, z' = b + x z, w' = -c z + d w``.
    S2 (Lorenz 1963): ``x' = sigma (y - x), y' = x (rho - z) - y,
    z' = x y - beta z``. S3 (Rossler 1976 with the state ordered (z, x, y)):
    ``z' = b + z (x - c), x' = -y - z, y' = x + a y``. S4 to S6: the relayed
    Dysts ``_rhs`` lines, typed in the branches below.
    """
    s = [float(v) for v in state]
    if name == "rossler_hyper":
        x, y, z, w = s
        terms = [
            [-y, -z],
            [x, p["a"] * y, w],
            [p["b"], x * z],
            [-p["c"] * z, p["d"] * w],
        ]
    elif name == "lorenz63_r166":
        x, y, z = s
        terms = [
            [p["sigma"] * y, -p["sigma"] * x],
            [x * p["rho"], -x * z, -y],
            [x * y, -p["beta"] * z],
        ]
    elif name == "rossler_z":
        z, x, y = s
        terms = [
            [p["b"], z * x, -z * p["c"]],
            [-y, -z],
            [x, p["a"] * y],
        ]
    elif name == "hindmarsh_rose":
        # Typed from the relay of Dysts ``HindmarshRose._rhs`` (researcher note
        # 2026-10-20, equations relay), lines 4 to 6 of the quoted class.
        x, y, z = s
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        sp, tx, tz = p["s"], p["tx"], p["tz"]
        terms = [
            [-x, 1 / tx * y, -a / tx * x**3, b / tx * x**2, 1 / tx * z],
            [-a * x**3, -(d - b) * x**2, z],
            [-sp / tz * x, -1 / tz * z, c / tz],
        ]
    elif name == "hyper_jha":
        # Relay of Dysts ``HyperJha._rhs`` (same note), lines 4 to 7.
        x, y, z, w = s
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        terms = [
            [a * y, -a * x, w],
            [-x * z, b * x, -y],
            [x * y, -c * z],
            [-x * z, d * w],
        ]
    else:
        # Relay of Dysts ``Lorenz96.rhs`` (same note), lines 4 to 7, written out
        # for N = 4 (``X[-2] = X2``, ``X[-1] = X3``, ``X[-3] = X1``, and the
        # slice ``Xdot[2:-1]`` is the single entry ``Xdot[2]``).
        x0, x1, x2, x3 = s
        f = p["F"]
        terms = [
            [(x1 - x2) * x3, -x0, f],
            [(x2 - x3) * x0, -x1, f],
            [(x3 - x0) * x1, -x2, f],
            [(x0 - x1) * x2, -x3, f],
        ]
    value = np.array([sum(t) for t in terms])
    scale = np.array([sum(abs(v) for v in t) for t in terms])
    return value, scale


def test_extension_fields_match_the_quoted_equations() -> None:
    """A1: each field equals a NumPy evaluation of the quoted equations.

    Reference: ``reference_field`` (equations in its docstring), evaluated in
    float64 NumPy at five dyadic states per system, independent of the code.

    Tolerance: ``|diff| <= K eps sum|terms|`` per component with ``K`` from
    ``TOLERANCE_FACTOR`` (derivation there: 4 for sums of at most three terms,
    8 for S4). For S4 to S6 the reference is the relayed Dysts code (the
    transcribed ``_rhs`` lines, which specification note 2 section 12 requires
    to be matched term by term), so this test is that match.
    """
    for name in EXTENSION:
        spec = SYSTEMS[name]
        for state in STATES[name]:
            got = np.asarray(
                spec.field_fn(jnp.asarray(state), spec.params), dtype=float
            )
            want, scale = reference_field(name, np.asarray(state), spec.params)
            assert got.shape == (spec.dim,)
            factor = TOLERANCE_FACTOR[name]
            assert np.all(np.abs(got - want) <= factor * EPS * scale), (
                name,
                state,
                got - want,
            )


def analytic_jacobian(name: str, state: tuple, p: dict) -> tuple:
    """Return the hand-derived Jacobian and its entrywise sum of |terms|."""
    if name == "rossler_hyper":
        x, y, z, w = state
        a, c, d = p["a"], p["c"], p["d"]
        jac = [
            [0.0, -1.0, -1.0, 0.0],
            [1.0, a, 0.0, 1.0],
            [z, 0.0, x, 0.0],
            [0.0, 0.0, -c, d],
        ]
        scale = [
            [0.0, 1.0, 1.0, 0.0],
            [1.0, abs(a), 0.0, 1.0],
            [abs(z), 0.0, abs(x), 0.0],
            [0.0, 0.0, abs(c), abs(d)],
        ]
    elif name == "lorenz63_r166":
        x, y, z = state
        sg, rho, bt = p["sigma"], p["rho"], p["beta"]
        jac = [[-sg, sg, 0.0], [rho - z, -1.0, -x], [y, x, -bt]]
        scale = [
            [abs(sg), abs(sg), 0.0],
            [abs(rho) + abs(z), 1.0, abs(x)],
            [abs(y), abs(x), abs(bt)],
        ]
    elif name == "rossler_z":
        z, x, y = state
        a, c = p["a"], p["c"]
        jac = [[x - c, z, 0.0], [-1.0, 0.0, -1.0], [0.0, 1.0, a]]
        scale = [
            [abs(x) + abs(c), abs(z), 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, abs(a)],
        ]
    elif name == "hindmarsh_rose":
        x, y, z = state
        a, b, d = p["a"], p["b"], p["d"]
        sp, tx, tz = p["s"], p["tx"], p["tz"]
        jac = [
            [-1.0 + (-3 * a * x**2 + 2 * b * x) / tx, 1 / tx, 1 / tx],
            [-3 * a * x**2 - 2 * (d - b) * x, 0.0, 1.0],
            [-sp / tz, 0.0, -1 / tz],
        ]
        scale = [
            [
                1.0 + (3 * a * x**2 + 2 * abs(b * x)) / tx,
                1 / tx,
                1 / tx,
            ],
            [3 * a * x**2 + 2 * abs((d - b) * x), 0.0, 1.0],
            [abs(sp) / tz, 0.0, 1 / tz],
        ]
    elif name == "hyper_jha":
        x, y, z, w = state
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        jac = [
            [-a, a, 0.0, 1.0],
            [-z + b, -1.0, -x, 0.0],
            [y, x, -c, 0.0],
            [-z, 0.0, -x, d],
        ]
        scale = [
            [abs(a), abs(a), 0.0, 1.0],
            [abs(z) + abs(b), 1.0, abs(x), 0.0],
            [abs(y), abs(x), abs(c), 0.0],
            [abs(z), 0.0, abs(x), abs(d)],
        ]
    else:
        # X_k' = (X_{k+1} - X_{k-2}) X_{k-1} - X_k + F, indices mod 4:
        # d/dX_{k+1} = X_{k-1}; d/dX_{k-2} = -X_{k-1}; d/dX_{k-1} =
        # X_{k+1} - X_{k-2}; d/dX_k = -1.
        n = 4
        jac = np.zeros((n, n))
        scale = np.zeros((n, n))
        for k in range(n):
            up, down, prev = (k + 1) % n, (k - 2) % n, (k - 1) % n
            jac[k, up] += state[prev]
            jac[k, down] -= state[prev]
            jac[k, prev] += state[up] - state[down]
            jac[k, k] -= 1.0
            scale[k, up] += abs(state[prev])
            scale[k, down] += abs(state[prev])
            scale[k, prev] += abs(state[up]) + abs(state[down])
            scale[k, k] += 1.0
    return np.array(jac), np.array(scale)


def test_extension_jacobians_match_the_analytic_ones() -> None:
    """A2: ``jax.jacfwd`` of each field equals the hand-written Jacobian.

    Reference: the partial derivatives of the equations of ``reference_field``,
    differentiated by hand in ``analytic_jacobian``, at the same states.

    Tolerance: ``|diff| <= K eps sum|terms|`` per entry, ``K`` from
    ``TOLERANCE_FACTOR`` (each entry is a sum of at most a few products;
    autodiff adds no truncation error).
    """
    for name in EXTENSION:
        spec = SYSTEMS[name]
        jac_fn = jax.jacfwd(lambda s, spec=spec: spec.field_fn(s, spec.params))
        for state in STATES[name]:
            got = np.asarray(jac_fn(jnp.asarray(state)), dtype=float)
            want, scale = analytic_jacobian(name, state, spec.params)
            assert got.shape == (spec.dim, spec.dim)
            factor = TOLERANCE_FACTOR[name]
            assert np.all(np.abs(got - want) <= factor * EPS * scale), (
                name,
                state,
            )


def test_s3_is_the_registry_rossler_with_permuted_coordinates() -> None:
    """S3's field is the registry Rossler field in the order (z, x, y).

    Reference: ``systems.rossler_field`` (the frozen field, an independent
    function from the new one). Tolerance: ``4 eps sum|terms|`` per component
    (``reference_field`` scale), since both evaluate the same expressions in
    float64 and the permutation only reorders them.
    """
    spec = SYSTEMS["rossler_z"]
    for z, x, y in STATES["rossler_z"]:
        got = np.asarray(
            spec.field_fn(jnp.asarray((z, x, y)), spec.params), dtype=float
        )
        classic = np.asarray(
            systems.rossler_field(jnp.asarray((x, y, z)), spec.params),
            dtype=float,
        )  # (x', y', z')
        _, scale = reference_field("rossler_z", np.asarray((z, x, y)), spec.params)
        want = np.array([classic[2], classic[0], classic[1]])
        assert np.all(np.abs(got - want) <= 4 * EPS * scale)


def test_divergence_identities_pin_the_transcribed_equations() -> None:
    """The trace of the Jacobian equals the closed-form divergence (S4 to S6).

    Reference (specification note 2, sections 6 and 12): S5
    ``-a - 1 - c + d`` (a constant, = -12.367), S6 ``-N`` = -4 exactly (the
    quadratic term never contains ``X_k`` itself), S4
    ``-1 + (2 b x - 3 a x^2) / tx - 1 / tz`` (state dependent). The sums are
    typed here from the equations, not read from the code; the trace is taken
    from ``jax.jacfwd`` of the code's field at the five dyadic states.

    Tolerance: ``K eps sum|terms|`` with ``K`` from ``TOLERANCE_FACTOR`` times
    the number of diagonal terms (a sum of ``m`` diagonal entries adds ``m - 1``
    roundings of the same size): 4 * 4 eps for S5 and S6, 8 * 3 eps for S4.
    """
    for name in ("hindmarsh_rose", "hyper_jha", "lorenz96_4"):
        spec = SYSTEMS[name]
        p = spec.params
        jac_fn = jax.jacfwd(lambda s, spec=spec: spec.field_fn(s, spec.params))
        for state in STATES[name]:
            trace = float(np.trace(np.asarray(jac_fn(jnp.asarray(state)))))
            if name == "hyper_jha":
                want = -p["a"] - 1.0 - p["c"] + p["d"]
                scale = p["a"] + 1.0 + p["c"] + p["d"]
            elif name == "lorenz96_4":
                want, scale = -4.0, 4.0
            else:
                x = state[0]
                want = (
                    -1.0
                    + (2 * p["b"] * x - 3 * p["a"] * x**2) / p["tx"]
                    - 1.0 / p["tz"]
                )
                scale = (
                    1.0
                    + (2 * abs(p["b"] * x) + 3 * p["a"] * x**2) / p["tx"]
                    + 1.0 / p["tz"]
                )
            bound = TOLERANCE_FACTOR[name] * spec.dim * EPS * scale
            assert abs(trace - want) <= bound, (name, state, trace, want)


# ------------------------------------------------------- A3 RK4 order


def _attractor_states(name: str, count: int) -> list[np.ndarray]:
    """Return ``count`` states of the orbit, 150 steps apart, after burn-in."""
    spec = SYSTEMS[name]
    interval = 1.0 / (30.0 * LAMBDA[name])
    flow = make_flow_step(spec, spec.params, interval)
    orbit = systems.simulate_trajectory(
        flow, jnp.asarray(spec.initial_state), 3000 + 150 * count
    )
    return [orbit[3000 + 150 * k] for k in range(count)]


# Substeps of the coarsest run over a horizon of half a Lyapunov time. The
# counts were fixed from a scan (T = 0.5 / 1 Lyapunov times, n = 20 ... 320, and
# up to 1280 for S2) before the test was written: they are the smallest counts
# in the table of the unit log for which the coarsest self-difference is below
# 1e-3 and the three observed orders are in the asymptotic range; the
# acceptance interval [3.8, 4.2] of the plan was not changed.
# After the S1 re-specification (new lambda, so new attractor states) the S1
# count was fixed again from a second scan (n = 160 gave orders 4.08, 4.43,
# 3.75; 320 gave 4.04, 4.30, 3.88; 640 gives 4.02, 4.18, 3.94; 1280 gives
# 4.01, 4.10, 3.97): 640 is the smallest count with all three in the interval.
COARSE_SUBSTEPS = {
    "rossler_hyper": 640,
    "lorenz63_r166": 640,
    "rossler_z": 160,
    # S4 to S6: the smallest count of the scan (n = 80 ... 1280, T = 0.5 LT) with
    # all three observed orders in [3.8, 4.2], fixed before the test was written
    # (S4: n = 80 gave 4.60, 3.88, 3.92, n = 160 gives 3.97, 3.94, 3.96; S5: 160
    # gave 4.09, 3.78, 3.73, 320 gives 4.05, 3.90, 3.89; S6: 80 gives 3.96,
    # 3.98, 4.04). Premise window met: e2 above 1e-11 and e1 below 1e-3.
    "hindmarsh_rose": 160,
    "hyper_jha": 320,
    "lorenz96_4": 80,
}


@pytest.mark.parametrize("name", EXTENSION)
def test_rk4_observed_order_is_four(name: str) -> None:
    """A3: RK4 on the new field has observed order 4 (Richardson).

    Reference: self-convergence. With the same horizon ``T = 0.5 / lambda``
    and ``n``, ``2n``, ``4n`` substeps, ``e1 = |x_n - x_2n|`` and ``e2 =
    |x_2n - x_4n|`` (max norm over the state), and the observed order
    ``log2(e1 / e2)`` (``e1 / e2 = 2^p`` for a leading error ``C h^p``). No
    closed-form solution exists, so no other reference is available (WU-0005.1
    uses the same method).

    Tolerance: the observed order in [3.8, 4.2] (plan A3), at every one of 3
    attractor states. Premise asserted: ``e2 > 1e-11`` (above round-off, about
    1e-13 for O(10) states over a few hundred steps) and ``e1 < 1e-3`` (so the
    leading term dominates).
    """
    spec = SYSTEMS[name]
    horizon = 0.5 / LAMBDA[name]
    states = jnp.asarray(np.stack(_attractor_states(name, 3)))

    def final(n: int) -> np.ndarray:
        # max_dt slightly above horizon / n so that ceil(horizon / max_dt) = n.
        tiny = dataclasses.replace(spec, max_dt=horizon / n * (1.0 + 1e-9))
        step = make_flow_step(tiny, spec.params, horizon)
        return np.asarray(jax.jit(jax.vmap(step))(states))

    n = COARSE_SUBSTEPS[name]
    coarse, middle, fine = final(n), final(2 * n), final(4 * n)
    e1 = np.max(np.abs(coarse - middle), axis=1)
    e2 = np.max(np.abs(middle - fine), axis=1)
    assert np.all(e2 > 1e-11), e2
    assert np.all(e1 < 1e-3), e1
    order = np.log2(e1 / e2)
    assert np.all((order >= 3.8) & (order <= 4.2)), order


# ------------------------------------------------------------- A4 V6


@pytest.mark.parametrize("name", EXTENSION)
def test_integrator_step_halving_meets_v6(name: str) -> None:
    """A4: halving ``max_dt`` changes x by less than 1e-3 sigma_x over 1 LT.

    Reference: the criterion of v3 section 6 (V6), not a computed value: over
    20 attractor states and 30 observation steps (1 Lyapunov time, the
    interval being ``1 / (30 lambda)``), ``max |x_h - x_{h/2}| / sigma_x <
    1e-3`` for the spec's ``max_dt`` h. The two flows are built with
    ``make_flow_step`` (the code's substep rule) and iterated with a scan
    written in this test.

    Tolerance: the criterion 1e-3 itself, unchanged. The specification note
    measured 1.1e-6 (S1), 1.7e-5 (S2) and 1.2e-4 (S3) on its own states.
    """
    spec = SYSTEMS[name]
    interval = 1.0 / (30.0 * LAMBDA[name])
    starts = jnp.asarray(np.stack(_attractor_states(name, 20)))
    coarse = make_flow_step(spec, spec.params, interval)
    fine = make_flow_step(
        dataclasses.replace(spec, max_dt=spec.max_dt / 2), spec.params, interval
    )

    def path(step, state):
        def body(s, _):
            nxt = step(s)
            return nxt, nxt[spec.observed_index]

        return jax.lax.scan(body, state, None, length=30)[1]

    a = np.asarray(jax.jit(jax.vmap(lambda s: path(coarse, s)))(starts))
    b = np.asarray(jax.jit(jax.vmap(lambda s: path(fine, s)))(starts))
    statistic = np.max(np.abs(a - b)) / SIGMA_X[name]
    assert np.isfinite(statistic)
    assert statistic < 1e-3, statistic


# ------------------------------------------------------------ A5 guard


@pytest.mark.parametrize("name", EXTENSION)
def test_guard_accepts_the_bound_and_refuses_above_it_and_nan(name: str) -> None:
    """A5: ``guard_orbit`` accepts |x| = B, refuses B(1 + 1e-9) and NaN.

    Reference: the guard's definition (closed bound, finite values), written
    out here with hand-built arrays. ``|x| = B`` is exactly representable, and
    ``B (1 + 1e-9)`` exceeds it by 1e-9 relative, 4e6 eps. Also checked: the
    positive and the negative side, a real orbit of 20 000 steps is accepted
    with its maximum below B (an exact comparison), and ``checked_bound``
    returns the spec's bound.
    """
    spec = SYSTEMS[name]
    bound = spec.orbit_bound
    assert checked_bound(spec) == bound
    base = np.zeros((5, spec.dim))
    for sign in (1.0, -1.0):
        at = base.copy()
        at[3, 0] = sign * bound
        assert guard_orbit(spec, "main", at) == bound
        above = base.copy()
        above[3, 0] = sign * bound * (1.0 + 1e-9)
        with pytest.raises(OrbitDivergence, match="step 3"):
            guard_orbit(spec, "main", above)
    for bad in (np.nan, np.inf):
        nonfinite = base.copy()
        nonfinite[2, spec.dim - 1] = bad  # a coordinate other than x
        with pytest.raises(OrbitDivergence, match="non-finite"):
            guard_orbit(spec, "main", nonfinite)
    interval = 1.0 / (30.0 * LAMBDA[name])
    orbit = systems.simulate_trajectory(
        make_flow_step(spec, spec.params, interval),
        jnp.asarray(spec.initial_state),
        20_000,
    )
    assert guard_orbit(spec, "statistics", orbit) < bound


def test_s3_keeps_the_observed_index_refusal() -> None:
    """S3 is a permuted-state spec: ``observed_index`` is 0 and 2 is refused.

    Reference: the ratified guard (DEC-0017 Q1, DEC-0026): the bound is on
    coordinate 0 only. S3 observes the Rossler z as its coordinate 0, so no
    exception is needed, and a spec with ``observed_index = 2`` is still
    refused.
    """
    spec = SYSTEMS["rossler_z"]
    assert spec.observed_index == 0
    with pytest.raises(ValueError, match="observed_index"):
        checked_bound(dataclasses.replace(spec, observed_index=2))


# ------------------------------------------------ the S2 bound (analytic)


def trapping_radius(sigma: float, rho: float, beta: float) -> float:
    """Return ``sqrt(max_E V)``, the largest |x| inside the trapping ball.

    With ``V = x^2 + y^2 + (z - sigma - rho)^2`` and ``c = sigma + rho``,
    ``dV/dt = -2 sigma x^2 - 2 y^2 - 2 beta (z - c/2)^2 + beta c^2 / 2``
    (checked numerically below), negative outside the ellipsoid E:
    ``sigma x^2 + y^2 + beta u^2 <= beta c^2 / 4`` with ``u = z - c/2``. The
    ball ``V <= max_E V`` is forward invariant, and ``x^2 <= V``. On E, for
    ``sigma > 1`` the maximum of ``V`` at a given ``u`` has ``x = 0`` and
    ``y^2 = beta (c^2/4 - u^2)``, so ``V(u) = beta (c^2/4 - u^2) + (u - c/2)^2``,
    a concave parabola (``beta > 1``) with its maximum at
    ``u = -c / (2 (beta - 1))``.
    """
    assert sigma > 1.0 and beta > 1.0
    c = sigma + rho
    u = -c / (2.0 * (beta - 1.0))
    assert abs(u) <= c / 2.0
    value = beta * (c * c / 4.0 - u * u) + (u - c / 2.0) ** 2
    return math.sqrt(value)


def test_lorenz_trapping_identity_and_the_s2_bound() -> None:
    """The S2 bound 185 is the trapping radius 181.88 rounded up.

    Reference: the identity ``dV/dt`` of ``trapping_radius`` is checked by a
    NumPy evaluation of the Lorenz field (not the code under test) at random
    states, to 1e-12 relative (round-off of a few terms of size 1e5). The
    radius is compared with the specification note's 181.88 (SLSQP and surface
    sampling, two decimals: tolerance 5e-3) and, for the registry, with the
    ratified 40 (radius 39.25 < 40 <= 40).

    Tolerance: the two-decimal rounding of the note; the closed form is exact
    up to round-off.
    """
    sigma, beta = 10.0, 8.0 / 3.0
    rng = np.random.default_rng(20261020)
    for rho in (28.0, 166.1):
        c = sigma + rho
        for _ in range(50):
            x, y, z = rng.normal(scale=100.0, size=3)
            dx, dy, dz = sigma * (y - x), x * (rho - z) - y, x * y - beta * z
            dv = 2 * (x * dx + y * dy + (z - c) * dz)
            closed = (
                -2 * sigma * x * x
                - 2 * y * y
                - 2 * beta * (z - c / 2) ** 2
                + beta * c * c / 2
            )
            assert abs(dv - closed) <= 1e-12 * (abs(dv) + abs(closed) + 1.0)
    assert abs(trapping_radius(sigma, 166.1, beta) - 181.88) < 5e-3
    assert abs(trapping_radius(sigma, 28.0, beta) - 39.25) < 5e-3
    assert 181.88 < SYSTEMS["lorenz63_r166"].orbit_bound == 185.0
    assert trapping_radius(sigma, 28.0, beta) < SYSTEMS["lorenz63"].orbit_bound


# ------------------------------------------- Lyapunov reference rows (R11)


def test_lyapunov_references_cover_every_registry_system() -> None:
    """R11: every registry system has a row; S1 has the published one.

    Reference: the specification note section 1.1 and section 7 R11,
    typed here: S1 0.1121 (Ramasubramanian and Sriram 1999, Table 1, standard
    method), tolerance 3%; S2 and S3 have no confirmed published value (empty
    list). The table builder compares the cached S1 value 0.11220509 with
    0.1121: the relative difference ``0.11220509 / 0.1121 - 1 = 0.000937`` is
    computed here by hand and must print as ``+0.09%`` and PASS (3% > 0.09%).

    Tolerance: none for the keys and constants; the printed text is exact.
    """
    from lpcstudy import report

    assert set(report.LYAPUNOV_REFERENCES) == set(SYSTEMS)
    rows = report.LYAPUNOV_REFERENCES["rossler_hyper"]
    assert len(rows) == 1
    assert rows[0][:2] == (0.1121, 0.03)
    assert "Ramasubramanian" in rows[0][2]
    assert report.LYAPUNOV_REFERENCES["lorenz63_r166"] == []
    assert report.LYAPUNOV_REFERENCES["rossler_z"] == []
    results = {
        "systems": {
            "rossler_hyper": {"context": {"lambda_max": LAMBDA["rossler_hyper"]}},
            "lorenz63_r166": {"context": {"lambda_max": LAMBDA["lorenz63_r166"]}},
        }
    }
    lines = report._lyapunov_lines(results, ["rossler_hyper", "lorenz63_r166"])
    hyper = [ln for ln in lines if ln.startswith("| rossler_hyper")]
    assert len(hyper) == 1 and "+0.09%" in hyper[0] and "PASS" in hyper[0]
    other = [ln for ln in lines if ln.startswith("| lorenz63_r166")]
    assert len(other) == 1
    assert "no confirmed published value" in other[0]


def test_lyapunov_rows_of_s4_to_s6_have_no_published_value() -> None:
    """S4 to S6 have empty reference lists and print the no-value row.

    Reference: specification note 2 section 6 (no published lambda for any of
    the three; the Dysts Lyapunov fields are not references) and the main
    session's brief: S6 is Lorenz-96 at N = 4, F = 20, and published Lorenz-96
    spectra for other N and F are not this system. Exact substring checks.
    """
    from lpcstudy import report

    names = ("hindmarsh_rose", "hyper_jha", "lorenz96_4")
    for name in names:
        assert report.LYAPUNOV_REFERENCES[name] == []
    results = {
        "systems": {n: {"context": {"lambda_max": LAMBDA[n]}} for n in names}
    }
    lines = report._lyapunov_lines(results, list(names))
    for name in names:
        row = [ln for ln in lines if ln.startswith(f"| {name} ")]
        assert len(row) == 1
        assert "no confirmed published value" in row[0]
        assert "DEC-0010" not in row[0]
        assert ("published Lorenz-96 spectra" in row[0]) == (
            name == "lorenz96_4"
        )
