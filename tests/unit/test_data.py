"""Seeded random streams (WU-0001.1)."""

from __future__ import annotations

import inspect
import json
import zlib

import numpy as np

from lpcstudy.config import SMOKE
from lpcstudy.data import build_context, make_rng
from lpcstudy.pipeline import Study
from lpcstudy.seeds import REGISTRY_PATH, with_seed


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


def test_every_random_state_keyword_is_a_sklearn_seed_call() -> None:
    """In ``lpcstudy/`` every ``random_state=`` keyword value is a ``sklearn_seed(...)`` call.

    Reference: the ``ast`` parse of every module (no import of the code under test); sites with
    a different value (a raw ``config.seed``, a name, a literal) fail the scan. At least four
    sites must exist (analysis x3, allocation x1), so the scan cannot pass vacuously.
    Tolerance: none. Scope: DEC-0008 B; the labels at the sites are also checked to be distinct
    string literals.
    """
    import ast
    from pathlib import Path

    package = Path(__file__).resolve().parents[2] / "lpcstudy"
    sites: list[str] = []
    bad: list[str] = []
    labels: list[str] = []
    for path in sorted(package.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg != "random_state":
                    continue
                where = f"{path.name}:{keyword.value.lineno}"
                sites.append(where)
                value = keyword.value
                func = value.func if isinstance(value, ast.Call) else None
                name = getattr(func, "id", getattr(func, "attr", None))
                if name != "sklearn_seed":
                    bad.append(where)
                    continue
                label = value.args[1] if len(value.args) == 2 else None
                if isinstance(label, ast.Constant) and isinstance(label.value, str):
                    labels.append(label.value)
                else:
                    bad.append(f"{where} (label is not a string literal)")
    assert len(sites) >= 4, sites
    assert not bad, f"random_state= not routed through sklearn_seed: {bad}"
    assert len(set(labels)) == len(labels), f"labels not distinct: {sorted(labels)}"
