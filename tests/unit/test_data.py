"""Seeded random streams (WU-0001.1)."""

from __future__ import annotations

import ast
import inspect
import json
import zlib

import numpy as np
import pytest

from lpcstudy.config import SMOKE
from lpcstudy.data import build_context, lyapunov_cached, make_rng
from lpcstudy.pipeline import Study
from lpcstudy.seeds import REGISTRY_PATH, with_seed
from lpcstudy.systems import (SYSTEMS, SystemSpec, chua_field, make_flow_step,
                              simulate_trajectory)


def test_make_rng_with_a_registry_seed_equals_numpy_directly() -> None:
    """``make_rng`` on a seed set by ``with_seed`` draws the stream NumPy gives for the key.

    Reference: ``np.random.default_rng([v, zlib.crc32(b"a|1")])``, NumPy used directly,
    with ``v`` the DEV-1 value read from the registry by ``json.load``. The streams are
    identical, so the comparison is exact (no tolerance), and the 62-bit seed is not
    narrowed on the way.
    """
    with REGISTRY_PATH.open() as handle:
        value = next(e["value"] for e in json.load(handle)["seeds"] if e["id"] == "DEV-1")
    config = with_seed(SMOKE, "DEV-1", value)
    assert config.seed == value
    ours = make_rng(config.seed, "a", 1).random(8)
    reference = np.random.default_rng([value, zlib.crc32(b"a|1")]).random(8)
    assert np.array_equal(ours, reference)


def test_no_delay_scale_parameter_remains() -> None:
    """``build_context``, ``Study.context`` and ``Study.run_cell`` have no ``delay_scale`` (WU-0002.1).

    Reference: the removal of the tau_d/2 robustness variant (v3 section 6, E6 lists D, k and
    +-5/10% only; Methods v2 section M15 item 9), written out in the test. Tolerance: none;
    equality of parameter-name sets (read with ``inspect.signature``). Recorded placement: this
    file, as the plan allows.
    """
    for function in (build_context, Study.context, Study.run_cell):
        assert "delay_scale" not in inspect.signature(function).parameters, function


# ---------------------------------------------------------------- sklearn_seed (WU-0002.6(a))

SKLEARN_LABELS = ("qn-regressor", "h3b-weight-tree", "h3b-horizon-tree", "regime-tree")
LIMIT = 2**32


def _registry_values(prefixes: tuple[str, ...]) -> dict[str, int]:
    """Registry seed values by id, read with ``json.load`` (independent of ``lpcstudy.seeds``)."""
    with REGISTRY_PATH.open() as handle:
        entries = json.load(handle)["seeds"]
    return {e["id"]: e["value"] for e in entries if e["id"] in prefixes}


def _numpy_derived(seed: int, label: str) -> int:
    """The derivation of DEC-0008 B written out with NumPy directly (not via ``make_rng``)."""
    key = zlib.crc32(f"sklearn|{label}".encode())
    return int(np.random.default_rng([seed, key]).integers(0, 2**32))


def test_sklearn_seed_below_the_limit_is_the_raw_seed() -> None:
    """0, the DEV-0 seed and 2**32 - 1 are returned unchanged, as ``int`` (DEC-0008 B).

    Reference: the rule of DEC-0008 B (identity below 2**32), written out. Tolerance: none;
    exact integer equality. The identity keeps every DEV-0 stream bitwise unchanged.
    """
    from lpcstudy.data import sklearn_seed

    for seed in (0, 20261005, LIMIT - 1):
        for label in SKLEARN_LABELS:
            out = sklearn_seed(seed, label)
            assert out == seed and type(out) is int


def test_sklearn_seed_at_and_above_the_limit_equals_numpy_derivation() -> None:
    """2**32 and DEV-1..4 give the NumPy-direct derived value, in sklearn's range, per label.

    Reference: ``np.random.default_rng([seed, crc32(b"sklearn|<label>")]).integers(0, 2**32)``
    built here without ``make_rng``; and ``sklearn.utils.check_random_state`` as the oracle of
    the accepted range (it raises ``ValueError`` for seeds outside [0, 2**32 - 1]). Tolerance:
    none; exact integers. The four labels give four distinct values for each large seed (the
    chance of any collision among 4 draws from 2**32 values is about 1.4e-9, and the values
    are fixed by the seed, so the assertion is deterministic).
    """
    from sklearn.utils import check_random_state

    from lpcstudy.data import sklearn_seed

    seeds = [LIMIT, *_registry_values(("DEV-1", "DEV-2", "DEV-3", "DEV-4")).values()]
    assert len(seeds) == 5 and all(s >= LIMIT for s in seeds)
    for seed in seeds:
        values = [sklearn_seed(seed, label) for label in SKLEARN_LABELS]
        assert values == [_numpy_derived(seed, label) for label in SKLEARN_LABELS]
        assert len(set(values)) == len(values)
        for value in values:
            assert 0 <= value < LIMIT
            check_random_state(value)  # raises ValueError if out of range


def test_sklearn_seed_pins_two_literals_and_is_deterministic() -> None:
    """Two derived values are pinned as literals, and repeated calls agree (DEC-0008 B).

    Reference: literals computed once with NumPy directly
    (``np.random.default_rng([seed, zlib.crc32(b"sklearn|qn-regressor")]).integers(0, 2**32)``)
    for seed 2**32 and for the DEV-1 registry value. This pins the mapping: a change of the
    derivation changes every large-seed run (it is a regression guard on the pin, with the
    independent derivation checked in the test above). Tolerance: exact.
    """
    from lpcstudy.data import sklearn_seed

    dev1 = _registry_values(("DEV-1",))["DEV-1"]
    assert dev1 == 2844678021587022684
    assert sklearn_seed(LIMIT, "qn-regressor") == 4244151644
    assert sklearn_seed(dev1, "qn-regressor") == 262068453
    assert sklearn_seed(dev1, "qn-regressor") == sklearn_seed(dev1, "qn-regressor")


def test_sklearn_seed_boundary_is_exactly_two_to_the_32() -> None:
    """2**32 - 1 is raw and 2**32 is derived (it differs from the input).

    Reference: sklearn's accepted range [0, 2**32 - 1] via ``check_random_state``: the raw
    2**32 raises there, the derived value does not. Tolerance: exact. The derived value of
    2**32 equals 2**32 itself with probability 2**-32 per label, and the labels are fixed.
    """
    import pytest
    from sklearn.utils import check_random_state

    from lpcstudy.data import sklearn_seed

    assert sklearn_seed(LIMIT - 1, "regime-tree") == LIMIT - 1
    with pytest.raises(ValueError):
        check_random_state(LIMIT)
    derived = sklearn_seed(LIMIT, "regime-tree")
    assert derived != LIMIT and derived == _numpy_derived(LIMIT, "regime-tree")
    check_random_state(derived)


def test_sklearn_seed_rejects_negative_seed_and_bad_types() -> None:
    """A negative seed raises ``ValueError``; a non-integer raises ``TypeError`` (PRIME.4).

    Reference: the contract of the plan (negative seed raises). Tolerance: none.
    """
    import pytest

    from lpcstudy.data import sklearn_seed

    with pytest.raises(ValueError, match="seed"):
        sklearn_seed(-1, "regime-tree")
    with pytest.raises(TypeError):
        sklearn_seed(1.5, "regime-tree")  # type: ignore[arg-type]


def _is_master_seed(node: ast.expr) -> bool:
    """True for the name ``seed`` or the attribute ``config.seed`` / ``cfg.seed``."""
    if isinstance(node, ast.Name):
        return node.id == "seed"
    return (isinstance(node, ast.Attribute) and node.attr == "seed"
            and isinstance(node.value, ast.Name) and node.value.id in ("config", "cfg"))


def _scan_random_state(sources: dict[str, str]) -> tuple[int, list[str]]:
    """Scan module sources for ``random_state=`` uses that bypass ``sklearn_seed``.

    Returns the number of ``random_state=`` sites and a list of problems. A site is accepted
    only if its value is ``sklearn_seed(<master seed>, "<literal label>")`` with the master seed
    the name ``seed`` or ``config.seed`` / ``cfg.seed`` (not a constant, an offset or another
    name) and the label a distinct string literal (distinct across all ``sources``). A call that
    carries a ``random_state=`` keyword and also ``**`` unpacking, or unpacks a dict literal with
    the key ``"random_state"``, is flagged too.
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
                if has_state or (isinstance(literal, ast.Dict) and any(
                        isinstance(key, ast.Constant) and key.value == "random_state"
                        for key in literal.keys)):
                    problems.append(f"{name}:{node.lineno} ** unpacking with random_state")
            for keyword in node.keywords:
                if keyword.arg != "random_state":
                    continue
                sites += 1
                value = keyword.value
                where = f"{name}:{value.lineno}"
                func = value.func if isinstance(value, ast.Call) else None
                callee = getattr(func, "id", getattr(func, "attr", None))
                if callee != "sklearn_seed" or value.keywords or len(value.args) != 2:
                    problems.append(f"{where} not a sklearn_seed(seed, label) call")
                    continue
                first, label = value.args
                if not _is_master_seed(first):
                    problems.append(f"{where} first argument is not the master seed")
                if not (isinstance(label, ast.Constant) and isinstance(label.value, str)):
                    problems.append(f"{where} label is not a string literal")
                elif label.value in labels:
                    problems.append(
                        f"{where} label {label.value!r} duplicates {labels[label.value]}")
                else:
                    labels[label.value] = where
    return sites, problems


def test_random_state_scan_flags_bypasses_and_passes_good_forms() -> None:
    """The scanner flags every bypass of ``sklearn_seed`` and passes the two accepted forms.

    Reference: hand-written source strings (not repository files) whose verdict is known by
    construction. Tolerance: none. Flagged: ``random_state=0``; ``random_state=config.seed``
    (raw seed); ``sklearn_seed(0, "y")`` (constant first argument); ``sklearn_seed(seed + 1,
    "z")`` (offset); ``sklearn_seed(other, "z")``; a duplicate label; a non-literal label; a
    ``**`` unpacking with ``random_state`` either as a keyword of the same call or as a key of
    a dict literal. Passed: ``sklearn_seed(seed, "x")`` and ``sklearn_seed(config.seed, "x")``
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
    duplicate = 'A(random_state=sklearn_seed(seed, "x"))\nB(random_state=sklearn_seed(seed, "x"))'
    sites, problems = _scan_random_state({"dup": duplicate})
    assert sites == 2 and len(problems) == 1 and "duplicates" in problems[0]
    sites, problems = _scan_random_state({"a": 'A(random_state=sklearn_seed(seed, "x"))',
                                          "b": 'B(random_state=sklearn_seed(config.seed, "w"))',
                                          "c": 'C(random_state=sklearn_seed(cfg.seed, "v"))',
                                          "d": "f(**kw)"})
    assert sites == 3 and problems == []


def test_every_random_state_keyword_is_a_sklearn_seed_call() -> None:
    """In ``lpcstudy/`` every ``random_state=`` value is ``sklearn_seed(<master seed>, "<label>")``.

    Reference: the ``ast`` parse of every module (no import of the code under test), by the
    scanner whose verdicts are tested on source strings above. The first argument must be the
    master seed (``seed``, ``config.seed`` or ``cfg.seed``), the label a distinct string
    literal, and no call may carry ``random_state`` together with ``**`` unpacking. At least
    four sites must exist (analysis x3, allocation x1), so the scan cannot pass vacuously.
    Tolerance: none. Scope: DEC-0008 B. Limit: a MISSING ``random_state`` keyword is not caught
    (scikit-learn then draws from the global NumPy state): telling whether an estimator needs a
    seed requires its class semantics, which an AST scan does not know, so that stays with the
    review and with the ``make_rng`` rule in numerical-code.md.
    """
    from pathlib import Path

    package = Path(__file__).resolve().parents[2] / "lpcstudy"
    sources = {path.name: path.read_text() for path in sorted(package.glob("*.py"))}
    sites, problems = _scan_random_state(sources)
    assert sites >= 4, sites
    assert not problems, f"random_state= not routed through sklearn_seed: {problems}"


# ------------------------------------------- lambda_max against published values (WU-0007.2)

# These three constants mirror the settings of ``lyapunov_cached`` (``lpcstudy/data.py``: the
# tangent step ``20 * spec.max_dt``, ``n_steps=100_000``, ``burn_in=5_000``). They are
# repeated here so that the orbit guard runs the same map for the same number of steps.
LYAPUNOV_STEP_FACTOR = 20
LYAPUNOV_AVERAGING_STEPS = 100_000
LYAPUNOV_BURN_IN_STEPS = 5_000

# The published Chua double-scroll set of the 1984 memo (UCB/ERL M84/73), in the dimensionless
# form of ``chua_field``: alpha = C2/C1 = 9, beta = C2/(L G^2) = 100/7, and the diode slopes
# divided by G = 0.7: inner m0 = -0.8/0.7 = -8/7, outer m1 = -0.5/0.7 = -5/7. NOT the study's
# Chua parameters. Same start, step and field as the registry Chua.
CHUA_MEMO = SystemSpec(
    name="chua_memo", field_fn=chua_field,
    params={"alpha": 9.0, "beta": 100.0 / 7.0, "m0": -8.0 / 7.0, "m1": -5.0 / 7.0},
    dim=3, observed_index=0, initial_state=(0.7, 0.0, 0.0), max_dt=0.005)

# (spec, [(published value per natural time unit, relative tolerance), ...], bound on |x|).
# The registry Chua has no reference: no confirmed published value exists at the study's
# parameters. The memo reference is 0.23 per circuit time t, divided by 0.7 (tau = 0.7 t).
LYAPUNOV_CASES = [
    pytest.param(SYSTEMS["lorenz63"], [(0.90563, 0.01)], 40.0, id="lorenz63"),
    pytest.param(SYSTEMS["rossler"], [(0.0714, 0.03), (0.07062, 0.03)], 25.0, id="rossler"),
    pytest.param(SYSTEMS["chua"], [], 3.0, id="chua"),
    pytest.param(CHUA_MEMO, [(0.23 / 0.7, 0.10)], 3.0, id="chua_memo"),
]


@pytest.mark.parametrize(("spec", "references", "bound"), LYAPUNOV_CASES)
def test_lyapunov_cached_matches_published_reference(spec: SystemSpec,
                                                     references: list[tuple[float, float]],
                                                     bound: float, tmp_path) -> None:
    """``lyapunov_cached`` agrees with the published lambda_max on a bounded orbit (WU-0007.2).

    Reference: LITERATURE values per natural time unit, independent of the code, and NOT the
    code's own pilot output (which Methods v2 rounds to 0.905, 0.0719 and 0.431). The
    comparison is in natural time units; the per-step lambda is 1/30 by construction and carries
    no information.

    - Lorenz-63 (sigma 10, rho 28, beta 8/3): 0.90563, Sprott, ``lespec.htm`` (confirmed;
      integrator and step not stated). Cross-check 0.905 +- 0.003, Hartl, arXiv:physics/0303077.
    - Rossler (a = b = 0.2, c = 5.7): 0.0714, Sprott as cited by Bogdanov and Bogdanova,
      arXiv:1412.2242 (secondary: Sprott's own text not retrieved), and 0.07062 +- 0.00066,
      Bogdanov and Bogdanova's own estimate (confirmed, primary). Both are asserted.
    - Chua (alpha 15.6, beta 28, m0 -1.143, m1 -0.714): NO confirmed published value (WU-0007.1,
      DEC-0010). There is NO lambda assertion: a known limitation, the exponent is not
      validated (NVVUQ.13). The case still asserts that the exponent is finite and that the orbit
      is bounded.
    - Chua memo set (``chua_memo``: alpha 9, beta 100/7, m0 -8/7 inner, m1 -5/7 outer; a
      DIFFERENT parameter set from the study's): mu_1 = 0.23 per circuit time t, Matsumoto,
      Chua and Komuro, memorandum UCB/ERL M84/73 (1984), eq. (3.14) and (3.19), memo
      parameters (1.3). The reference is DERIVED from the memo: tau = G t / C2 = 0.7 t, so
      0.23 / 0.7 = 0.3286 per dimensionless time. It is confirmed to two digits, with a weak
      second source, Martins (2016), SBMAC proceedings, DOI 10.5540/03.2016.004.01.0098, which
      states 0.33 for this set (algorithm, step and error bar not stated). This case validates
      the routine and the field form, NOT the study's Chua parameters. The memo's mu_3 (-0.28),
      exponent sum (-0.05) and Kaplan-Yorke dimension (2.82) are internally contradictory in
      the memo itself (the sum must equal the mean divergence, about -1.54 per t) and are
      deliberately NOT asserted.

    Tolerances, fixed before the result was seen (the applied-mathematician's DEVELOPMENT
    standard errors at 10^5 Benettin steps, burn-in 5000; no observed gap was used):

    - Lorenz 1%: code SE 0.0012 (0.13%); Sprott's own uncertainty is unstated, so Hartl's
      +-0.003 (0.33%) stands in. 3 * sqrt(0.13^2 + 0.33^2) = 1.06%. The RK4 bias is below 1e-4
      relative (h = 0.01 against 0.02 and 0.04 shows no trend).
    - Rossler 3% against each reference: code SE 0.00055 (0.75%), B&B 0.93%, combined
      sqrt(0.75^2 + 0.93^2) = 1.19%, so 3% is about 2.5 sigma (a family-wise false-alarm
      probability of at most about 2%). It cannot be tightened on SE grounds. The two references
      differ by 1.1%. The RK4 bias at h = 0.04 is about -0.1%.
    - Chua memo set 10%: code SE 0.0050 (1.5%), memo finite-T SE 3.3% (T = 3000 t = 2100 tau),
      rounding of "0.23" (SD 1.3%), discretization below 1.5%: combined sigma about 3.9%, so
      10% is about 2.6 sigma. It cannot be tightened. The code's value at this set had been seen
      in development before the tolerance was fixed; the 10% rests on the error budget alone.

    Orbit guard (DEF-0015): ``estimate_lyapunov`` returns a finite, positive, plausible value for
    a diverging orbit, so "finite and positive" detects nothing. Each case therefore simulates
    its own orbit (the same map ``make_flow_step(spec, spec.params, 20 * max_dt)``, the same
    start state, 5000 + 10^5 steps) and asserts every value is finite and the first coordinate
    obeys max|x| <= B. B = 3 for Chua, both parameter sets (attractor |x| <= 2.26; the start
    (0.7, 0, 0) is inside the double-scroll basin for both, whereas about 3 of 12 perturbed starts
    leave it). B = 40 for Lorenz: the ball
    x^2 + y^2 + (z - sigma - rho)^2 <= (39.25)^2 is forward invariant for the ODE and the start
    (1, 1, 1) is inside, so |x| <= 39.25, and the margin absorbs the RK4 error. B = 25 for
    Rossler: no trapping region is known; an escaping orbit has x > c persistently and
    z' = b + z (x - c) overflows within 10^5 steps, so any bound well above the attractor
    separates the cases. The bound is not to be raised to pass.

    Runtime: about 1 s per case including JIT, within the unit budget.
    """
    system = spec.name
    interval = LYAPUNOV_STEP_FACTOR * spec.max_dt
    value = lyapunov_cached(spec, tmp_path / "lyapunov.json")
    assert np.isfinite(value), f"{system}: lambda_max is not finite"
    for reference, tolerance in references:
        gap = value / reference - 1.0
        assert abs(gap) <= tolerance, (
            f"{system}: lambda_max {value:.6g} against published {reference} is {gap:+.2%} "
            f"(tolerance {tolerance:.0%}); the step {interval} is the suspected cause "
            "(LPC.NV.1); report, do not tune")
    orbit = simulate_trajectory(make_flow_step(spec, spec.params, interval),
                                np.asarray(spec.initial_state, dtype=np.float64),
                                LYAPUNOV_BURN_IN_STEPS + LYAPUNOV_AVERAGING_STEPS)
    assert np.isfinite(orbit).all(), f"{system}: the orbit left the finite range (diverged)"
    largest = float(np.abs(orbit[:, spec.observed_index]).max())
    assert largest <= bound, f"{system}: max|x| = {largest:.4g} exceeds the bound {bound}"
