"""Tests for ``lpcstudy.data``: seeded random streams, the Lyapunov cache, start
states.

``data`` builds the trajectories and units that every experiment uses, and it
owns ``make_rng``, the only source of random numbers in the package. The tests
here check four things:

* ``make_rng`` and ``sklearn_seed`` give the streams that NumPy gives when
  called directly (WU-0001.1, WU-0002.6);
* the largest Lyapunov exponent agrees with published values, and its disk
  cache refuses bad entries (WU-0007.2, WU-0002.11c);
* the seed-drawn start states of the trajectories follow the documented
  recipe (WU-0002.14);
* ``build_context`` records digests and guard values in ``ctx.meta``.

Each test names its independent reference and the reason for its tolerance.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
import json
import math
import re
import struct
import tempfile
import zlib
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import sqrtm
from sklearn.utils import check_random_state

from lpcstudy import data as data_module
from lpcstudy.config import SMOKE
from lpcstudy.data import build_context, lyapunov_record, make_rng, sklearn_seed
from lpcstudy.pipeline import Study
from lpcstudy.seeds import REGISTRY_PATH, with_seed
from lpcstudy.systems import (
    SYSTEMS,
    OrbitDivergence,
    SystemSpec,
    chua_field,
    make_flow_step,
    simulate_trajectory,
)


def test_make_rng_with_a_registry_seed_equals_numpy_directly() -> None:
    """``make_rng`` with a registry seed draws the same stream as NumPy does.

    Reference: ``np.random.default_rng([v, zlib.crc32(b"a|1")])``, NumPy used
    directly, with ``v`` the DEV-1 value read from the registry by
    ``json.load``. The streams are identical, so the comparison is exact (no
    tolerance), and the 62-bit seed is not narrowed on the way.
    """
    with REGISTRY_PATH.open() as handle:
        value = next(
            e["value"] for e in json.load(handle)["seeds"] if e["id"] == "DEV-1"
        )
    config = with_seed(SMOKE, "DEV-1", value)
    assert config.seed == value
    ours = make_rng(config.seed, "a", 1).random(8)
    reference = np.random.default_rng([value, zlib.crc32(b"a|1")]).random(8)
    assert np.array_equal(ours, reference)


def test_no_delay_scale_parameter_remains() -> None:
    """The removed ``delay_scale`` option is gone from the public functions
    (WU-0002.1).

    ``build_context``, ``Study.context`` and ``Study.run_cell`` must not accept
    ``delay_scale``.

    Reference: the removal of the tau_d/2 robustness variant (v3 section 6, E6
    lists D, k and +-5/10% only; Methods v2 section M15 item 9), written out in
    the test. Tolerance: none; the parameter names are read with
    ``inspect.signature`` and compared as sets. Recorded placement: this file,
    as the plan allows.
    """
    for function in (build_context, Study.context, Study.run_cell):
        assert (
            "delay_scale" not in inspect.signature(function).parameters
        ), function


# sklearn_seed: seeds that scikit-learn accepts (WU-0002.6(a))

SKLEARN_LABELS = (
    "qn-regressor",
    "h3b-weight-tree",
    "h3b-horizon-tree",
    "regime-tree",
)
LIMIT = 2**32


def _registry_values(prefixes: tuple[str, ...]) -> dict[str, int]:
    """Return the registry seed values for some ids, read with plain
    ``json.load``.

    This is independent of ``lpcstudy.seeds``, so tests can trust it.
    """
    with REGISTRY_PATH.open() as handle:
        entries = json.load(handle)["seeds"]
    return {e["id"]: e["value"] for e in entries if e["id"] in prefixes}


def _numpy_derived(seed: int, label: str) -> int:
    """Write out the derivation of DEC-0008 B with NumPy directly (not
    ``make_rng``).
    """
    key = zlib.crc32(f"sklearn|{label}".encode())
    return int(np.random.default_rng([seed, key]).integers(0, 2**32))


def test_sklearn_seed_below_the_limit_is_the_raw_seed() -> None:
    """Seeds below 2**32 pass through ``sklearn_seed`` unchanged, as ``int``.

    The seeds 0, the DEV-0 seed and 2**32 - 1 are checked (DEC-0008 B).

    Reference: the rule of DEC-0008 B (identity below 2**32), written out.
    Tolerance: none (exact integer equality). The identity keeps every DEV-0
    stream bitwise unchanged.
    """

    for seed in (0, 20261005, LIMIT - 1):
        for label in SKLEARN_LABELS:
            out = sklearn_seed(seed, label)
            assert out == seed and type(out) is int


def test_sklearn_seed_at_and_above_the_limit_equals_numpy_derivation() -> None:
    """Seeds of 2**32 and above give the NumPy-derived value, in scikit-learn's
    range.

    The seeds checked are 2**32 and DEV-1..4, for each label.

    Reference: ``np.random.default_rng([seed, crc32(b"sklearn|<label>")])
    .integers(0, 2**32)`` built here without ``make_rng``; and
    ``sklearn.utils.check_random_state`` as the oracle of the accepted range (it
    raises ``ValueError`` for seeds outside [0, 2**32 - 1]). Tolerance: none
    (exact integers). The four labels give four distinct values for each large
    seed (the chance of any collision among 4 draws from 2**32 values is about
    1.4e-9, and the values are fixed by the seed, so the assertion is
    deterministic).
    """

    seeds = [
        LIMIT,
        *_registry_values(("DEV-1", "DEV-2", "DEV-3", "DEV-4")).values(),
    ]
    assert len(seeds) == 5 and all(s >= LIMIT for s in seeds)
    for seed in seeds:
        values = [sklearn_seed(seed, label) for label in SKLEARN_LABELS]
        assert values == [
            _numpy_derived(seed, label) for label in SKLEARN_LABELS
        ]
        assert len(set(values)) == len(values)
        for value in values:
            assert 0 <= value < LIMIT
            check_random_state(value)  # raises ValueError if out of range


def test_sklearn_seed_pins_two_literals_and_is_deterministic() -> None:
    """Two derived values are pinned as literals, and repeated calls agree
    (DEC-0008 B).

    Reference: literals computed once with NumPy directly
    (``np.random.default_rng([seed, zlib.crc32(b"sklearn|qn-regressor")])
    .integers(0, 2**32)``) for seed 2**32 and for the DEV-1 registry value. This
    pins the mapping: a change of the derivation changes every large-seed run.
    It is a regression guard on the pin; the independent derivation is checked
    in the test above. Tolerance: exact.
    """

    dev1 = _registry_values(("DEV-1",))["DEV-1"]
    assert dev1 == 2844678021587022684
    assert sklearn_seed(LIMIT, "qn-regressor") == 4244151644
    assert sklearn_seed(dev1, "qn-regressor") == 262068453
    assert sklearn_seed(dev1, "qn-regressor") == sklearn_seed(
        dev1,
        "qn-regressor",
    )


def test_sklearn_seed_boundary_is_exactly_two_to_the_32() -> None:
    """The seed 2**32 - 1 is returned as is, and 2**32 is replaced by a derived
    value.

    Reference: scikit-learn's accepted range [0, 2**32 - 1] via
    ``check_random_state``: the raw 2**32 raises there, the derived value does
    not. Tolerance: exact. The derived value of 2**32 equals 2**32 itself with
    probability 2**-32 per label, and the labels are fixed.
    """

    assert sklearn_seed(LIMIT - 1, "regime-tree") == LIMIT - 1
    with pytest.raises(ValueError):
        check_random_state(LIMIT)
    derived = sklearn_seed(LIMIT, "regime-tree")
    assert derived != LIMIT and derived == _numpy_derived(LIMIT, "regime-tree")
    check_random_state(derived)


def test_sklearn_seed_rejects_negative_seed_and_bad_types() -> None:
    """A negative seed raises ``ValueError`` and a non-integer raises
    ``TypeError``.

    Bad input must fail loudly (PRIME.4). Reference: the contract of the plan (a
    negative seed raises). Tolerance: none.
    """

    with pytest.raises(ValueError, match="seed"):
        sklearn_seed(-1, "regime-tree")
    with pytest.raises(TypeError):
        sklearn_seed(1.5, "regime-tree")  # type: ignore[arg-type]


def _is_master_seed(node: ast.expr) -> bool:
    """Say whether a syntax node is the master seed (``seed``, ``config.seed``
    or ``cfg.seed``).
    """
    if isinstance(node, ast.Name):
        return node.id == "seed"
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "seed"
        and isinstance(node.value, ast.Name)
        and node.value.id in ("config", "cfg")
    )


def _scan_random_state(sources: dict[str, str]) -> tuple[int, list[str]]:
    """Scan module sources for ``random_state=`` uses that bypass
    ``sklearn_seed``.

    Returns the number of ``random_state=`` sites and a list of problems. A site
    is accepted only if its value is ``sklearn_seed(<master seed>, "<literal
    label>")``, where the master seed is the name ``seed`` or ``config.seed`` /
    ``cfg.seed`` (not a constant, an offset or another name) and the label is a
    distinct string literal (distinct across all ``sources``). A call that
    carries a ``random_state=`` keyword and also ``**`` unpacking, or unpacks a
    dict literal with the key ``"random_state"``, is flagged too.
    """
    sites = 0
    problems: list[str] = []
    labels: dict[str, str] = {}
    for name, source in sources.items():
        for node in ast.walk(ast.parse(source, filename=name)):
            if not isinstance(node, ast.Call):
                continue
            has_state = any(k.arg == "random_state" for k in node.keywords)
            for keyword in node.keywords:
                if keyword.arg is not None:
                    continue
                literal = keyword.value
                if has_state or (
                    isinstance(literal, ast.Dict)
                    and any(
                        isinstance(key, ast.Constant)
                        and key.value == "random_state"
                        for key in literal.keys
                    )
                ):
                    problems.append(
                        f"{name}:{node.lineno} ** unpacking with random_state"
                    )
            for keyword in node.keywords:
                if keyword.arg != "random_state":
                    continue
                sites += 1
                value = keyword.value
                where = f"{name}:{value.lineno}"
                func = value.func if isinstance(value, ast.Call) else None
                callee = getattr(func, "id", getattr(func, "attr", None))
                if (
                    callee != "sklearn_seed"
                    or value.keywords
                    or len(value.args) != 2
                ):
                    problems.append(
                        f"{where} not a sklearn_seed(seed, label) call"
                    )
                    continue
                first, label = value.args
                if not _is_master_seed(first):
                    problems.append(
                        f"{where} first argument is not the master seed"
                    )
                if not (
                    isinstance(label, ast.Constant)
                    and isinstance(label.value, str)
                ):
                    problems.append(f"{where} label is not a string literal")
                elif label.value in labels:
                    problems.append(
                        f"{where} label {label.value!r} duplicates "
                        f"{labels[label.value]}"
                    )
                else:
                    labels[label.value] = where
    return sites, problems


def test_random_state_scan_flags_bypasses_and_passes_good_forms() -> None:
    """The scanner flags every bypass of ``sklearn_seed`` and passes the good
    forms.

    Reference: hand-written source strings (not repository files) whose verdict
    is known by construction. Tolerance: none.

    Flagged: ``random_state=0``; ``random_state=config.seed`` (raw seed);
    ``sklearn_seed(0, "y")`` (constant first argument); ``sklearn_seed(seed + 1,
    "z")`` (offset); ``sklearn_seed(other, "z")``; a duplicate label; a
    non-literal label; a ``**`` unpacking with ``random_state`` either as a
    keyword of the same call or as a key of a dict literal.

    Passed: ``sklearn_seed(seed, "x")`` and ``sklearn_seed(config.seed, "x")``
    (also ``cfg.seed``).
    """
    bad_sources = {
        "const": "M(random_state=0)",
        "raw": "M(random_state=config.seed)",
        "const_seed": 'M(random_state=sklearn_seed(0, "y"))',
        "offset": 'M(random_state=sklearn_seed(seed + 1, "z"))',
        "other_name": 'M(random_state=sklearn_seed(other, "z"))',
        "nonliteral_label": "M(random_state=sklearn_seed(seed, name))",
        "kw_label": 'M(random_state=sklearn_seed(seed, label="x"))',
        "unpack_dict": 'M(**{"random_state": config.seed})',
        "unpack_with_state": 'M(random_state=sklearn_seed(seed, "x"), **kw)',
    }
    for name, source in bad_sources.items():
        _, problems = _scan_random_state({name: source})
        assert problems, f"{name} was not flagged"
    duplicate = (
        'A(random_state=sklearn_seed(seed, "x"))\n'
        'B(random_state=sklearn_seed(seed, "x"))'
    )
    sites, problems = _scan_random_state({"dup": duplicate})
    assert sites == 2 and len(problems) == 1 and "duplicates" in problems[0]
    sites, problems = _scan_random_state(
        {
            "a": 'A(random_state=sklearn_seed(seed, "x"))',
            "b": 'B(random_state=sklearn_seed(config.seed, "w"))',
            "c": 'C(random_state=sklearn_seed(cfg.seed, "v"))',
            "d": "f(**kw)",
        }
    )
    assert sites == 3 and problems == []


def test_every_random_state_keyword_is_a_sklearn_seed_call() -> None:
    """Every ``random_state=`` in ``lpcstudy/`` is ``sklearn_seed(<master seed>,
    "<label>")``.

    Why: scikit-learn estimators must take their randomness from the study's
    master seed, so a run is repeatable (DEC-0008 B).

    Reference: the ``ast`` parse of every module (no import of the code under
    test), by the scanner whose verdicts are tested on source strings above. The
    first argument must be the master seed (``seed``, ``config.seed`` or
    ``cfg.seed``), the label a distinct string literal, and no call may carry
    ``random_state`` together with ``**`` unpacking. At least four sites must
    exist (analysis x3, allocation x1), so the scan cannot pass vacuously.
    Tolerance: none.

    Limit: a MISSING ``random_state`` keyword is not caught (scikit-learn then
    draws from the global NumPy state). Telling whether an estimator needs a
    seed requires its class semantics, which an AST scan does not know, so that
    stays with the review and with the ``make_rng`` rule in numerical-code.md.
    """

    package = Path(__file__).resolve().parents[2] / "lpcstudy"
    sources = {
        path.name: path.read_text() for path in sorted(package.glob("*.py"))
    }
    sites, problems = _scan_random_state(sources)
    assert sites >= 4, sites
    assert (
        not problems
    ), f"random_state= not routed through sklearn_seed: {problems}"


# lambda_max against published values (WU-0007.2)

# These three constants mirror the settings of ``lyapunov_record``
# (``lpcstudy/data.py``: the tangent step ``20 * spec.max_dt``,
# ``n_steps=100_000``, ``burn_in=5_000``). They are repeated here so that the
# orbit guard runs the same map for the same number of steps.
LYAPUNOV_STEP_FACTOR = 20
LYAPUNOV_AVERAGING_STEPS = 100_000
LYAPUNOV_BURN_IN_STEPS = 5_000

# The published Chua double-scroll set of the 1984 memo (UCB/ERL M84/73), in the
# dimensionless form of ``chua_field``: alpha = C2/C1 = 9, beta = C2/(L G^2) =
# 100/7, and the diode slopes divided by G = 0.7: inner m0 = -0.8/0.7 = -8/7,
# outer m1 = -0.5/0.7 = -5/7. NOT the study's Chua parameters. Same start, step
# and field as the registry Chua.
CHUA_MEMO = SystemSpec(
    name="chua_memo",
    field_fn=chua_field,
    params={
        "alpha": 9.0,
        "beta": 100.0 / 7.0,
        "m0": -8.0 / 7.0,
        "m1": -5.0 / 7.0,
    },
    dim=3,
    observed_index=0,
    initial_state=(0.7, 0.0, 0.0),
    max_dt=0.005,
    orbit_bound=3.0,
)

# (spec, [(published value per natural time unit, relative tolerance), ...],
# bound on |x|). The registry Chua has no reference: no confirmed published
# value exists at the study's parameters. The memo reference is 0.23 per circuit
# time t, divided by 0.7 (tau = 0.7 t).
LYAPUNOV_CASES = [
    pytest.param(SYSTEMS["lorenz63"], [(0.90563, 0.01)], 40.0, id="lorenz63"),
    pytest.param(
        SYSTEMS["rossler"],
        [(0.0714, 0.03), (0.07062, 0.03)],
        25.0,
        id="rossler",
    ),
    pytest.param(SYSTEMS["chua"], [], 3.0, id="chua"),
    pytest.param(CHUA_MEMO, [(0.23 / 0.7, 0.10)], 3.0, id="chua_memo"),
]


@pytest.mark.parametrize(("spec", "references", "bound"), LYAPUNOV_CASES)
def test_lyapunov_record_matches_published_reference(
    spec: SystemSpec,
    references: list[tuple[float, float]],
    bound: float,
    tmp_path,
) -> None:
    """``lyapunov_record`` agrees with the published lambda_max on a bounded
    orbit (WU-0007.2).

    The Lyapunov exponent measures how fast tiny errors grow. It sets the
    study's time unit, so a wrong value would silently rescale everything.

    Reference: LITERATURE values per natural time unit, independent of the code,
    and NOT the code's own pilot output (which Methods v2 rounds to 0.905,
    0.0719 and 0.431). The comparison is in natural time units; the per-step
    lambda is 1/30 by construction and carries no information.

    * Lorenz-63 (sigma 10, rho 28, beta 8/3): 0.90563, Sprott, ``lespec.htm``
      (confirmed; integrator and step not stated). Cross-check 0.905 +- 0.003,
      Hartl, arXiv:physics/0303077.
    * Rossler (a = b = 0.2, c = 5.7): 0.0714, Sprott as cited by Bogdanov and
      Bogdanova, arXiv:1412.2242 (secondary: Sprott's own text not retrieved),
      and 0.07062 +- 0.00066, Bogdanov and Bogdanova's own estimate (confirmed,
      primary). Both are asserted.
    * Chua (alpha 15.6, beta 28, m0 -1.143, m1 -0.714): NO confirmed published
      value (WU-0007.1, DEC-0010). There is NO lambda assertion: a known
      limitation, the exponent is not validated (NVVUQ.13). The case still
      asserts that the exponent is finite and that the orbit is bounded.
    * Chua memo set (``chua_memo``: alpha 9, beta 100/7, m0 -8/7 inner, m1 -5/7
      outer; a DIFFERENT parameter set from the study's): mu_1 = 0.23 per
      circuit
      time t, Matsumoto, Chua and Komuro, memorandum UCB/ERL M84/73 (1984), eq.
      (3.14) and (3.19), memo parameters (1.3). The reference is DERIVED from
      the
      memo: tau = G t / C2 = 0.7 t, so 0.23 / 0.7 = 0.3286 per dimensionless
      time. It is confirmed to two digits, with a weak second source, Martins
      (2016), SBMAC proceedings, DOI 10.5540/03.2016.004.01.0098, which states
      0.33 for this set (algorithm, step and error bar not stated). This case
      validates the routine and the field form, NOT the study's Chua parameters.
      The memo's mu_3 (-0.28), exponent sum (-0.05) and Kaplan-Yorke dimension
      (2.82) are internally contradictory in the memo itself (the sum must equal
      the mean divergence, about -1.54 per t) and are deliberately NOT asserted.

    Tolerances are derived from the error budget alone, with no observed gap
    used (the applied-mathematician's DEVELOPMENT standard errors at 10^5
    Benettin steps, burn-in 5000). The code's pilot values for Lorenz and
    Rossler were already visible when they were derived (VV.3), so they are not
    blind; the memo value was measured before the 10% was confirmed:

    * Lorenz 1%: code SE 0.0012 (0.13%); Sprott's own uncertainty is unstated,
      so Hartl's +-0.003 (0.33%) stands in. 3 * sqrt(0.13^2 + 0.33^2) = 1.06%.
      The RK4 bias is below 1e-4 relative (h = 0.01 against 0.02 and 0.04 shows
      no trend).
    * Rossler 3% against each reference: code SE 0.00055 (0.75%), B&B 0.93%,
      combined sqrt(0.75^2 + 0.93^2) = 1.19%, so 3% is about 2.5 sigma (a
      family-wise false-alarm probability of at most about 2%). It cannot be
      tightened on SE grounds. The two references differ by 1.1%. The RK4 bias
      at
      h = 0.04 is about -0.1%.
    * Chua memo set 10%: code SE 0.0050 (1.5%), memo finite-T SE 3.3% (T = 3000
      t
      = 2100 tau), rounding of "0.23" (SD 1.3%), discretization below 1.5%:
      combined sigma about 3.9%, so 10% is about 2.6 sigma. It cannot be
      tightened. The code's value at this set had been seen in development
      before
      the tolerance was fixed; the 10% rests on the error budget alone.

    Orbit guard (DEF-0015): ``estimate_lyapunov`` returns a finite, positive,
    plausible value for a diverging orbit, so "finite and positive" detects
    nothing. Each case therefore simulates its own orbit (the same map
    ``make_flow_step(spec, spec.params, 20 * max_dt)``, the same start state,
    5000 + 10^5 steps) and asserts every value is finite and the first
    coordinate obeys max|x| <= B.

    * B = 3 for Chua, both parameter sets (attractor |x| <= 2.26; the start
      (0.7, 0, 0) is inside the double-scroll basin for both, whereas about 3 of
      12 perturbed starts leave it).
    * B = 40 for Lorenz: the ball x^2 + y^2 + (z - sigma - rho)^2 <= (39.25)^2
      is
      forward invariant for the ODE and the start (1, 1, 1) is inside, so |x| <=
      39.25, and the margin absorbs the RK4 error.
    * B = 25 for Rossler: no trapping region is known; an escaping orbit has x >
      c
      persistently and z' = b + z (x - c) overflows within 10^5 steps, so any
      bound well above the attractor separates the cases.

    The bound is not to be raised to pass. Runtime: about 1 s per case including
    JIT, within the unit budget.
    """
    system = spec.name
    interval = LYAPUNOV_STEP_FACTOR * spec.max_dt
    value = lyapunov_record(spec, tmp_path / "lyapunov.json")[0]
    assert np.isfinite(value), f"{system}: lambda_max is not finite"
    # WU-0002.11c: the cache now holds the exponent and the orbit maximum under
    # the guard.
    stored = json.loads((tmp_path / "lyapunov.json").read_text())[system]
    assert (
        set(stored) == {"lambda_max", "orbit_max_abs"}
        and stored["lambda_max"] == value
    )
    assert 0.0 < stored["orbit_max_abs"] <= bound
    for reference, tolerance in references:
        gap = value / reference - 1.0
        assert abs(gap) <= tolerance, (
            f"{system}: lambda_max {value:.6g} against published {reference} "
            f"is {gap:+.2%} "
            f"(tolerance {tolerance:.0%}); the step {interval} is the "
            f"suspected cause "
            "(LPC.NV.1); report, do not tune"
        )
    orbit = simulate_trajectory(
        make_flow_step(spec, spec.params, interval),
        np.asarray(spec.initial_state, dtype=np.float64),
        LYAPUNOV_BURN_IN_STEPS + LYAPUNOV_AVERAGING_STEPS,
    )
    assert np.isfinite(
        orbit
    ).all(), f"{system}: the orbit left the finite range (diverged)"
    largest = float(np.abs(orbit[:, spec.observed_index]).max())
    assert (
        largest <= bound
    ), f"{system}: max|x| = {largest:.4g} exceeds the bound {bound}"


# Orbit guard in the data layer (WU-0002.11c).
#
# Needs owner review before freeze (the guard sets the study's time unit).
# References are hand JSON, hand arrays and the literal key lists of the plan
# (G6 to G8); none is read from the code.

LORENZ_CACHE = {
    "lambda_max": 0.9054940534657817,
    "orbit_max_abs": 19.267721702218743,
}
"""This host's values of the Lorenz-63 Benettin run.

They come from the applied-mathematician (M4 and M2); the pilot baseline lambda
is the same double. They are used only as inputs to the cache and to the
fake-trajectory tests, never as expected results of a computation."""


def _write_cache(path, **entries) -> None:
    """Write ``entries`` as a JSON cache file (hand-made input for the cache
    tests).
    """
    path.write_text(json.dumps(entries))


def test_build_context_refuses_a_failing_trajectory(
    monkeypatch,
    tmp_path,
) -> None:
    """G6: each of the three trajectories is guarded, and a failing one refuses
    the build.

    The guard covers burn-in too. Reference: hand-corrupted copies of the real
    array: x = 40 + 1e-6 at row 7 (statistics), a NaN in z only at row 11 (main)
    and +inf in y only at row 3 (estimator). Tolerance: none; the message must
    name that orbit and the first failing row, and no context is returned. The
    exponent is read from a pre-written new-form cache entry so that only the
    trajectory simulation runs (a unit test of the guard wiring, not of the
    dynamics).
    """
    _write_cache(tmp_path / "lyapunov.json", lorenz63=LORENZ_CACHE)
    real = simulate_trajectory
    cases = [
        (
            "statistics",
            0,
            7,
            (7, 0, 40.0 + 1e-6),
            re.escape(f"max|x| {40.0 + 1e-6:.17g}"),
        ),
        ("main", 1, 11, (11, 2, math.nan), r"max\|x\| non-finite"),
        ("estimator", 2, 3, (3, 1, math.inf), r"max\|x\| non-finite"),
    ]
    for orbit, target, row, (r, c, value), size in cases:
        calls = []

        def fake(
            step_fn,
            initial,
            n_steps,
            target=target,
            r=r,
            c=c,
            value=value,
        ):
            states = np.array(real(step_fn, initial, n_steps))
            calls.append(n_steps)
            if len(calls) == target + 1:
                states[r, c] = value
            return states

        monkeypatch.setattr(data_module, "simulate_trajectory", fake)
        with pytest.raises(
            OrbitDivergence,
            match=rf"orbit '{orbit}' of 'lorenz63'.*"
            rf"first failing step {row}, {size}",
        ):
            build_context("lorenz63", SMOKE, tmp_path)
        assert len(calls) == target + 1


def test_build_context_meta_has_the_four_new_leaves() -> None:
    """G8: ``ctx.meta`` has exactly the documented keys, with the right types
    and ranges.

    The keys added over time are ``lyapunov_orbit_max_abs`` and
    ``trajectory_max_abs``; since WU-0002.14, ``start_index`` and
    ``start_state`` (2 + 6 leaves, checked in the last block); since WU-0003.7a,
    the two trajectory digests ``main_digest`` and ``estimator_digest`` (their
    values are checked in ``test_build_context_trajectory_digests_...``).

    Reference: the literal key lists of the plan (4 leaves per system: the
    exponent orbit and the three trajectories). Tolerance: none for the key sets
    and types. Values are Python floats, at most B = 40 and at least the start
    (|x_0| = 1). The Lorenz-63 attractor gives max|x| in the band [18, 20]
    (block maxima of 3.2e6 states, M4) for each trajectory of 2e5 or more states
    (the estimator orbit of the smoke preset is shorter, so only the bound is
    asserted for it). A cache is written in the new form.
    """

    with tempfile.TemporaryDirectory() as folder:
        ctx = build_context("lorenz63", SMOKE, Path(folder))
        stored = json.loads((Path(folder) / "lyapunov.json").read_text())[
            "lorenz63"
        ]
    meta = ctx.meta
    assert set(meta) == {
        "lambda_max",
        "interval",
        "delay",
        "ami_delay",
        "embed_dim",
        "acf_time",
        "spacing",
        "obs_scale",
        "trajectory_len",
        "library_len",
        "theiler",
        "lyapunov_orbit_max_abs",
        "trajectory_max_abs",
        "start_index",
        "start_state",
        "main_digest",
        "estimator_digest",
    }
    assert set(meta["trajectory_max_abs"]) == {
        "statistics",
        "main",
        "estimator",
    }
    leaves = [
        meta["lyapunov_orbit_max_abs"],
        *meta["trajectory_max_abs"].values(),
    ]
    assert all(type(v) is float and 1.0 <= v <= 40.0 for v in leaves), leaves
    assert 18.0 <= meta["lyapunov_orbit_max_abs"] <= 20.0
    assert 18.0 <= meta["trajectory_max_abs"]["statistics"] <= 20.0
    assert stored == {
        "lambda_max": meta["lambda_max"],
        "orbit_max_abs": meta["lyapunov_orbit_max_abs"],
    }
    # WU-0002.14: the 8 start leaves per system (2 integer indices, 2 x 3
    # floats), JSON types
    assert (
        set(meta["start_index"])
        == set(meta["start_state"])
        == {"main", "estimator"}
    )
    for name in ("main", "estimator"):
        assert (
            type(meta["start_index"][name]) is int
            and 0 <= meta["start_index"][name] < 200_000
        )
        assert len(meta["start_state"][name]) == 3
        assert all(
            type(v) is float and abs(v) <= 40.0
            for v in meta["start_state"][name]
        )
    json.dumps(meta, allow_nan=False)


def _stub_guarded(monkeypatch, result=(0.5, 1.25)) -> list:
    """Replace ``data.lyapunov_guarded`` by a stub returning ``result``; return
    its call log.
    """
    calls: list = []

    def stub(spec, interval, n_steps, burn_in):
        calls.append((spec.name, interval, n_steps, burn_in))
        return result

    monkeypatch.setattr(data_module, "lyapunov_guarded", stub)
    return calls


def test_cache_migrates_a_legacy_entry_with_a_bitwise_check(
    monkeypatch,
    tmp_path,
) -> None:
    """G7 (a), (b): a legacy flat float is recomputed once and rewritten; one
    ulp more raises.

    Reference: hand JSON with a stubbed guarded recomputation returning (0.5,
    1.25). (The real equality of the bits is the regression test of
    ``test_systems`` and the V4 log check.) Tolerance: none, IEEE bytes.

    (a) A legacy 0.5 is accepted. The file becomes ``{"lambda_max": 0.5,
    "orbit_max_abs": 1.25}`` with the other system's entry untouched. The
    recomputation uses the production settings (interval 20 max_dt, 10^5 steps,
    burn-in 5000) and runs once.

    (b) ``nextafter(0.5, 1)`` raises ``RuntimeError`` and the file is unchanged.
    """
    calls = _stub_guarded(monkeypatch)
    cache = tmp_path / "lyapunov.json"
    spec = SYSTEMS["rossler"]
    _write_cache(cache, rossler=0.5, chua=0.25)
    assert lyapunov_record(spec, cache) == (0.5, 1.25)
    assert json.loads(cache.read_text()) == {
        "rossler": {"lambda_max": 0.5, "orbit_max_abs": 1.25},
        "chua": 0.25,
    }
    assert calls == [("rossler", 20 * spec.max_dt, 100_000, 5_000)]
    assert lyapunov_record(spec, cache) == (0.5, 1.25) and len(calls) == 1

    bumped = math.nextafter(0.5, 1.0)
    assert struct.pack("<d", bumped) != struct.pack("<d", 0.5)
    _write_cache(cache, rossler=bumped)
    before = cache.read_text()
    with pytest.raises(RuntimeError, match="differs from the recomputation"):
        lyapunov_record(spec, cache)
    assert cache.read_text() == before


def test_cache_new_form_entry_does_not_recompute(monkeypatch, tmp_path) -> None:
    """G7 (c): a new-form entry is returned as stored, with no recomputation.

    Reference: hand JSON. ``lyapunov_guarded`` is stubbed to raise if called. A
    missing entry is computed once and written in the new form. Tolerance: none.
    """

    def boom(*args, **kwargs):
        raise AssertionError("recomputed a cached entry")

    monkeypatch.setattr(data_module, "lyapunov_guarded", boom)
    cache = tmp_path / "sub" / "lyapunov.json"
    cache.parent.mkdir()
    _write_cache(cache, lorenz63=LORENZ_CACHE)
    assert lyapunov_record(SYSTEMS["lorenz63"], cache) == (
        0.9054940534657817,
        19.267721702218743,
    )
    calls = _stub_guarded(monkeypatch, result=(0.25, 2.0))
    assert (
        lyapunov_record(SYSTEMS["chua"], cache) == (0.25, 2.0)
        and len(calls) == 1
    )
    assert json.loads(cache.read_text()) == {
        "lorenz63": LORENZ_CACHE,
        "chua": {"lambda_max": 0.25, "orbit_max_abs": 2.0},
    }


def test_cache_refuses_a_spec_without_a_bound_and_bad_entries(
    monkeypatch,
    tmp_path,
) -> None:
    """G7 (d) and malformed entries raise; nothing is recomputed or rewritten
    silently.

    Reference: hand JSON. Tolerance: none. A spec with ``orbit_bound=None``
    raises ``ValueError`` even when the cache holds an entry for it. An entry
    with a missing key, a string, a bool, or an ``orbit_max_abs`` above B or NaN
    is refused (``ValueError`` or ``OrbitDivergence``).
    """
    calls = _stub_guarded(monkeypatch)
    cache = tmp_path / "lyapunov.json"
    unbounded = dataclasses.replace(SYSTEMS["lorenz63"], orbit_bound=None)
    _write_cache(cache, lorenz63=LORENZ_CACHE)
    with pytest.raises(ValueError, match="orbit_bound"):
        lyapunov_record(unbounded, cache)
    with pytest.raises(ValueError, match="orbit_bound"):
        lyapunov_record(unbounded, tmp_path / "absent.json")
    spec = SYSTEMS["lorenz63"]
    for entry in (
        {"lambda_max": 0.9},
        {"lambda_max": 0.9, "orbit_max_abs": 1.0, "x": 1.0},
        {"lambda_max": 0.9, "orbit_max_abs": 1},
        "0.9",
        True,
        [0.9],
    ):
        _write_cache(cache, lorenz63=entry)
        with pytest.raises(ValueError, match="malformed"):
            lyapunov_record(spec, cache)
    for largest in (math.nextafter(40.0, math.inf), 1e300):
        _write_cache(
            cache,
            lorenz63={"lambda_max": 0.9, "orbit_max_abs": largest},
        )
        with pytest.raises(OrbitDivergence, match="exceeds the bound 40"):
            lyapunov_record(spec, cache)
    cache.write_text('{"lorenz63": {"lambda_max": 0.9, "orbit_max_abs": NaN}}')
    with pytest.raises(OrbitDivergence, match="exceeds the bound 40"):
        lyapunov_record(spec, cache)
    assert calls == []


# Seed-drawn start states (WU-0002.14, P1 to P3, P8).  Seed code: needs owner
# review before freeze. References: NumPy used directly for the draws (the
# pattern of ``test_make_rng_with_a_registry_seed_equals_numpy_directly``),
# ``scipy.linalg`` for the matrix root (independent of
# ``data._symmetric_root``), and the formulas of the plan and its mathematics
# check (M1(e) for the tolerance of P3).

N_STATS = 200_000
ETA = 1e-6
# A 62-bit seed (the size of the registry and confirmatory seeds).
BIG_SEED = 4611686018427387847


def _synthetic_orbit() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Make a synthetic statistics orbit (200 000 x 3) with ``C^{1/2}`` and
    ``C^{-1/2}``.

    The roots come from ``scipy.linalg.sqrtm``, independent of the code under
    test.
    """

    rng = np.random.default_rng(14001)
    factor = rng.standard_normal((3, 3))
    cov = factor @ factor.T + 0.5 * np.eye(3)
    stats = rng.standard_normal((N_STATS, 3)) @ np.linalg.cholesky(
        cov
    ).T + np.array([1.0, -2.0, 8.0])
    root = np.real(sqrtm(np.cov(stats.T)))
    return stats, root, np.linalg.inv(root)


def test_draw_starts_is_deterministic_and_depends_on_seed_and_system() -> None:
    """P1: equal inputs give equal starts; another seed or system gives other
    starts.

    "Another seed" includes a 62-bit one. Reference: the property itself (the
    same call twice; distinct seeds and systems). The indices are compared as
    integers, the states by IEEE bytes. Two distinct indices out of 200 000
    collide with probability 5e-6 per pair, so the inequality assertions are
    deterministic for these fixed seeds (checked when the test was written, not
    tuned). Tolerance: none.
    """
    stats, root, _ = _synthetic_orbit()
    base = data_module.draw_starts(20261005, "lorenz63", stats, root)
    again = data_module.draw_starts(20261005, "lorenz63", stats, root)
    assert (
        base.main_index == again.main_index
        and base.estimator_index == again.estimator_index
    )
    assert base.main_state.tobytes() == again.main_state.tobytes()
    assert base.estimator_state.tobytes() == again.estimator_state.tobytes()
    for other in (
        data_module.draw_starts(1, "lorenz63", stats, root),
        data_module.draw_starts(BIG_SEED, "lorenz63", stats, root),
        data_module.draw_starts(20261005, "rossler", stats, root),
    ):
        assert (other.main_index, other.estimator_index) != (
            base.main_index,
            base.estimator_index,
        )
        assert other.main_state.tobytes() != base.main_state.tobytes()
    assert (
        base.main_index != base.estimator_index
    )  # the two starts are independent draws
    assert (
        data_module.draw_starts(BIG_SEED, "lorenz63", stats, root).main_index
        < N_STATS
    )


def test_draw_starts_consumes_one_generator_in_the_documented_order() -> None:
    """P2 and P3(a): a hand re-draw of ``k_main, u_main, k_est, u_est`` gives
    the same starts.

    Reference: ``np.random.default_rng([seed, crc32(b"start|<system>")])``
    (NumPy used directly): ``integers(0, n)``, ``standard_normal(3)``,
    ``integers(0, n)``, ``standard_normal(3)``, and the start ``stats[k] + eta *
    (C^{1/2} @ u)`` in that operation order. Exact: the indices as integers and
    the states bitwise (the same IEEE operations in the same order). Three
    seeds, one of them 62 bits.
    """
    stats, root, _ = _synthetic_orbit()
    for seed in (20261005, 7, BIG_SEED):
        got = data_module.draw_starts(seed, "chua", stats, root)
        ref = np.random.default_rng([seed, zlib.crc32(b"start|chua")])
        k_main = int(ref.integers(0, N_STATS))
        u_main = ref.standard_normal(3)
        k_est = int(ref.integers(0, N_STATS))
        u_est = ref.standard_normal(3)
        assert (got.main_index, got.estimator_index) == (k_main, k_est)
        assert (
            got.main_state.tobytes()
            == (stats[k_main] + ETA * (root @ u_main)).tobytes()
        )
        assert (
            got.estimator_state.tobytes()
            == (stats[k_est] + ETA * (root @ u_est)).tobytes()
        )
        assert got.main_state.dtype == np.float64


def test_draw_starts_support_and_norm_identity() -> None:
    """P3(b): the index is in range and the start is ``eta`` away from its orbit
    point.

    In symbols: ``0 <= k < n`` and ``| ||C^{-1/2}(s - stats[k])|| - eta ||u|| |
    <= T``, with T derived below.

    Reference: the draws ``k`` and ``u`` re-drawn by hand with NumPy, ``W =
    C^{-1/2}`` from scipy. The tolerance is the bound derived by the mathematics
    check (M1(e)): the subtraction ``s - a`` recovers ``delta = eta C^{1/2} u``
    only up to the rounding of the addition, ``|e_i| <= (eps/2)|s_i|``, so ``T =
    2 [ ||W||_2 (eps/2) ||s||_2 + 8 eps kappa_2(C^{1/2}) eta ||u|| ]`` with
    ``eps = 2.2e-16`` (the factor 2 is the margin; the worst measured case was
    0.87 of the bracket). The plan's 1e-12 relative tolerance is not used: a
    correct implementation fails it on 95 to 98 percent of the draws (asserted
    below as the reason for the correction). 300 seeds, two starts each.
    Tolerance: ``<= T`` exactly as derived.
    """
    stats, root, whiten = _synthetic_orbit()
    eps = 2.2e-16
    spectral = np.linalg.norm(whiten, 2)
    kappa = np.linalg.cond(root, 2)
    worst, over_plan = 0.0, 0
    for seed in range(300):
        got = data_module.draw_starts(seed, "lorenz63", stats, root)
        ref = np.random.default_rng([seed, zlib.crc32(b"start|lorenz63")])
        for index, state in (
            (got.main_index, got.main_state),
            (got.estimator_index, got.estimator_state),
        ):
            assert 0 <= index < N_STATS
            ref.integers(0, N_STATS)
            u = ref.standard_normal(3)
            shift = eta_norm = ETA * np.linalg.norm(u)
            err = abs(
                np.linalg.norm(whiten @ (state - stats[index])) - eta_norm
            )
            bound = 2.0 * (
                spectral * (eps / 2.0) * np.linalg.norm(state)
                + 8.0 * eps * kappa * shift
            )
            worst = max(worst, err / bound)
            over_plan += err > 1e-12 * eta_norm
    assert worst <= 1.0, worst
    assert (
        over_plan / 600 > 0.5
    ), over_plan  # the plan's 1e-12 relative bound would fail these


@pytest.fixture(scope="module")
def smoke_context(tmp_path_factory):
    """Build one smoke-size Lorenz-63 context once, and record the trajectories
    it simulated.

    The trajectories are returned in call order: statistics, main, estimator.
    """
    cache = tmp_path_factory.mktemp("lyapunov")
    _write_cache(cache / "lyapunov.json", lorenz63=LORENZ_CACHE)
    recorded = []
    real = data_module.simulate_trajectory

    def spy(step_fn, initial, n_steps):
        out = real(step_fn, initial, n_steps)
        recorded.append(out)
        return out

    data_module.simulate_trajectory = spy
    try:
        ctx = build_context("lorenz63", SMOKE, cache)
    finally:
        data_module.simulate_trajectory = real
    return ctx, recorded


def test_build_context_starts_are_drawn_burned_in_and_recorded(
    smoke_context,
) -> None:
    """P8: the first post-burn-in state of each data trajectory matches a hand
    burn-in, bitwise.

    Reference: ``simulate_trajectory(step, s, burn + 1)[burn]`` run in the test
    from the recorded start ``s`` (the burn-in done independently of
    ``build_context``), with ``step`` from ``make_flow_step``. The statistics
    orbit recomputed in the test gives ``draw_starts`` the same ``stats``, and
    the recorded indices and states must equal its output.

    Also checked: the trajectories are simulated in the order statistics, main,
    estimator; the main orbit has ``burn + trajectory_len`` states and
    ``trajectory_len`` is unchanged by the burn-in (the ``total`` of the
    layout); the statistics orbit starts at the registry state. Tolerance: none
    (bitwise).
    """
    ctx, recorded = smoke_context
    spec = SYSTEMS["lorenz63"]
    burn = int(SMOKE.burn_in_lyapunov * SMOKE.steps_per_lyapunov)
    step = make_flow_step(spec, spec.params, ctx.interval)
    stats_full, main_full, est_full = recorded
    assert np.array_equal(stats_full[0], spec.initial_state)
    assert len(main_full) == burn + ctx.meta["trajectory_len"]
    assert len(ctx.eval_states) == ctx.meta["trajectory_len"]
    starts = data_module.draw_starts(
        SMOKE.seed,
        "lorenz63",
        stats_full[burn:],
        ctx.unwhiten,
    )
    assert ctx.meta["start_index"] == {
        "main": starts.main_index,
        "estimator": starts.estimator_index,
    }
    assert ctx.meta["start_state"] == {
        "main": starts.main_state.tolist(),
        "estimator": starts.estimator_state.tolist(),
    }
    assert main_full[0].tobytes() == starts.main_state.tobytes()
    assert est_full[0].tobytes() == starts.estimator_state.tobytes()
    for name, full, first in (
        ("main", main_full, ctx.eval_states[0]),
        ("estimator", est_full, est_full[burn]),
    ):
        start = starts.main_state if name == "main" else starts.estimator_state
        burned = simulate_trajectory(step, start, burn + 1)[burn]
        assert full[burn].tobytes() == burned.tobytes(), name
        assert first.tobytes() == burned.tobytes(), name
    assert ctx.meta["trajectory_max_abs"]["main"] == float(
        np.max(np.abs(main_full[:, 0]))
    )


def test_build_context_trajectory_digests_are_sha256(
    smoke_context,
) -> None:
    """WU-0003.7a (a2): the two trajectory digests are the SHA-256 of the
    post-burn-in orbits.

    The orbits are the main and estimator trajectories, float64, C order.

    Reference: the trajectories that ``simulate_trajectory`` returned to
    ``build_context`` (recorded by the spy of ``smoke_context``, in call order
    statistics, main, estimator), cut at the burn-in in the test, and
    ``hashlib.sha256`` of their values packed with ``struct`` (little-endian
    binary64, row-major), written here and not through numpy ``tobytes`` or
    ``array_digest``. The main orbit is also ``ctx.eval_states`` (the digest of
    the stored array equals it). Not equal: the digest of the main orbit with
    its burn-in, the other trajectory and the statistics orbit (so the burn-in
    cut is load-bearing). Exact (a digest is a deterministic function of the
    bytes; no tolerance).
    """
    ctx, recorded = smoke_context
    burn = int(SMOKE.burn_in_lyapunov * SMOKE.steps_per_lyapunov)
    stats_full, main_full, est_full = recorded

    def reference(orbit: np.ndarray) -> str:
        assert orbit.dtype == np.float64 and orbit.ndim == 2
        values = orbit.ravel().tolist()
        return hashlib.sha256(
            struct.pack("<%dd" % len(values), *values)
        ).hexdigest()

    main_ref, est_ref = reference(main_full[burn:]), reference(est_full[burn:])
    assert ctx.meta["main_digest"] == main_ref == reference(ctx.eval_states)
    assert ctx.meta["estimator_digest"] == est_ref
    others = {
        reference(main_full),
        reference(est_full),
        reference(stats_full[burn:]),
    }
    assert len({main_ref, est_ref} | others) == 5
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", ctx.meta[k])
        for k in ("main_digest", "estimator_digest")
    )
    json.dumps(ctx.meta, allow_nan=False)


def test_the_start_does_not_depend_on_the_embedding_dimension(tmp_path) -> None:
    """M3: contexts of one system with different ``D`` share the same start.

    This gives common random numbers across the robustness sweep.

    Reference: the property. ``build_context`` at D = 7 (the smoke default) and
    D = 5 record the same indices and start states bitwise, and their main
    trajectories are the same states (the start and the burn-in do not depend on
    D; the layout differs, the orbit prefix does not). Tolerance: none.
    """
    _write_cache(tmp_path / "lyapunov.json", lorenz63=LORENZ_CACHE)
    seven = build_context("lorenz63", SMOKE, tmp_path)
    five = build_context("lorenz63", SMOKE, tmp_path, embed_dim=5)
    assert seven.meta["start_index"] == five.meta["start_index"]
    assert seven.meta["start_state"] == five.meta["start_state"]
    n = min(len(seven.eval_states), len(five.eval_states))
    assert seven.eval_states[:n].tobytes() == five.eval_states[:n].tobytes()
