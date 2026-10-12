"""Randomness hygiene of ``lpcstudy/`` (WU-0002.14, P4 and P5; DEF-0011; needs owner review
before freeze).

Two static scans of the package, each tested first on hand-written source strings whose verdict is
known by construction (the pattern of ``test_data.py``, ``_scan_random_state``), then run on the
repository:

* P4 (no bypass): ``default_rng(`` occurs only at the four allowlisted sites; no ``seed +``
  arithmetic; no use of ``np.random`` other than ``Generator`` and ``default_rng``; every
  ``PRNGKey(`` argument is a draw ``int(<generator>.integers(...))``, directly or through a name
  assigned from one in the same function.
* P5 (label hygiene): no literal label tuple of ``make_rng`` is used at two call sites, except
  the pairings that the design keeps on purpose (M4 of the mathematics check); and the crc32 of
  every label string of the full preset is distinct, because a crc collision would make two
  ``make_rng`` streams identical.

References are the allowlists written below, from the plan and its mathematics check, and the
independent ``zlib.crc32``. Tolerance: none (exact set equalities).
"""

from __future__ import annotations

import ast
import itertools
import zlib
from pathlib import Path

import numpy as np

from lpcstudy.config import FULL
from lpcstudy.data import make_rng

PACKAGE = Path(__file__).resolve().parents[2] / "lpcstudy"

DEFAULT_RNG_ALLOWLIST = {
    ("data.py", "make_rng"),
    ("statistics.py", "block_resample_indices"),  # the integer path, kept for fixtures
    ("validation.py", "check_cramer_rao"),  # V2 fixture, DEC-0017 Q7
    ("validation.py", "check_kaplan_meier"),  # V5 fixture, DEC-0017 Q7
}
"""The four ``default_rng(`` sites of the plan (P4)."""

PAIRINGS = {
    ("bootstrap", "H1b"): {("analysis.py", "h1b_seed_amplifier")},  # CP and PLP
    ("bootstrap", "H2c"): {("analysis.py", "h2c_state_dependence")},  # the three differences
    ("h2a-two-part",): {("analysis.py", "h2a_separation"),
                        ("experiments.py", "_perturbation_scale_variant")},  # H2a(ii), its variant
}
"""Literal label tuples that two ``make_rng`` call sites share on purpose (M4): the pairing of the
H1b CP and PLP resamples, of the three H2c differences, and of H2a(ii) with its Lambda_fin
variant. Every other pairing (H1c, Q-N, the directions across scales, the oracle pool, the
estimator and allocator streams) shares by calling ONE site more than once, which this scan
cannot see; ``test_analysis.py`` and ``test_experiments.py`` pin those (P9)."""


def _enclosing(tree: ast.AST) -> dict[ast.AST, str]:
    """Map every node to the name of the function that contains it ('<module>' outside one)."""
    owner: dict[ast.AST, str] = {}

    def visit(node: ast.AST, name: str) -> None:
        for child in ast.iter_child_nodes(node):
            child_name = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                else name
            owner[child] = child_name
            visit(child, child_name)

    owner[tree] = "<module>"
    visit(tree, "<module>")
    return owner


def _is_seed(node: ast.expr) -> bool:
    """True for the name ``seed`` or an attribute named ``seed`` (``config.seed``)."""
    return (isinstance(node, ast.Name) and node.id == "seed") or (
        isinstance(node, ast.Attribute) and node.attr == "seed")


def _is_generator_draw(node: ast.expr) -> bool:
    """True for ``int(<expr>.integers(...))``."""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "int" and len(node.args) == 1
            and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Attribute)
            and node.args[0].func.attr == "integers")


def scan_bypass(sources: dict[str, str]) -> tuple[set[tuple[str, str]], list[str]]:
    """Find the ``default_rng`` sites and the other bypasses of ``make_rng`` in module sources.

    Returns
    -------
    tuple[set[tuple[str, str]], list[str]]
        The set of ``(module, function)`` that call ``default_rng``, and the problems found:
        ``seed +`` arithmetic, ``np.random`` attributes other than ``Generator`` and
        ``default_rng``, a ``random`` import, and ``PRNGKey`` arguments that are not draws.
    """
    sites: set[tuple[str, str]] = set()
    problems: list[str] = []
    for module, source in sources.items():
        tree = ast.parse(source)
        owner = _enclosing(tree)
        draws: dict[tuple[str, str], bool] = {}  # (function, name) -> assigned only from draws
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                key = (owner[node], node.targets[0].id)
                draws[key] = draws.get(key, True) and _is_generator_draw(node.value)
        for node in ast.walk(tree):
            where = f"{module}:{getattr(node, 'lineno', '?')}"
            if isinstance(node, ast.Call):
                func = node.func
                callee = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                if callee == "default_rng":
                    sites.add((module, owner[node]))
                if callee == "PRNGKey":
                    arg = node.args[0] if len(node.args) == 1 and not node.keywords else None
                    ok = arg is not None and (
                        _is_generator_draw(arg) or (isinstance(arg, ast.Name)
                                                    and draws.get((owner[node], arg.id), False)))
                    if not ok:
                        problems.append(f"{where} PRNGKey argument is not a Generator draw")
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and (
                    _is_seed(node.left) or _is_seed(node.right)):
                problems.append(f"{where} seed arithmetic")
            elif isinstance(node, ast.Attribute) and node.attr not in ("Generator", "default_rng") \
                    and isinstance(node.value, ast.Attribute) and node.value.attr == "random" \
                    and isinstance(node.value.value, ast.Name) \
                    and node.value.value.id in ("np", "numpy"):
                problems.append(f"{where} np.random.{node.attr}")
            elif isinstance(node, ast.Import) and any(a.name == "random" for a in node.names):
                problems.append(f"{where} import random")
            elif isinstance(node, ast.ImportFrom) and node.module == "random":
                problems.append(f"{where} from random import")
    return sites, problems


def scan_labels(sources: dict[str, str]) -> list[tuple[str, str, int, tuple[str, ...]]]:
    """List ``(module, function, line, literal labels)`` of every ``make_rng`` call.

    The literal labels are the string constants (and the source of f-strings) among the
    arguments after the seed. A call with a ``*labels`` argument is not listed; its callers are:
    the tuple argument of ``_paired_change`` is read as the labels of that call.
    """
    found = []
    for module, source in sources.items():
        tree = ast.parse(source)
        owner = _enclosing(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = node.func.id if isinstance(node.func, ast.Name) \
                else getattr(node.func, "attr", None)
            if callee == "make_rng" and not any(isinstance(a, ast.Starred) for a in node.args[1:]):
                parts = node.args[1:]
            elif callee == "_paired_change":
                parts = next((a.elts for a in node.args if isinstance(a, ast.Tuple)), None)
                if parts is None:
                    continue
            else:
                continue
            literal = tuple(
                p.value if isinstance(p, ast.Constant) and isinstance(p.value, str)
                else ast.unparse(p) for p in parts
                if (isinstance(p, ast.Constant) and isinstance(p.value, str))
                or isinstance(p, ast.JoinedStr))
            found.append((module, owner[node], node.lineno, literal))
    return found


def shared_labels(found: list[tuple[str, str, int, tuple[str, ...]]]
                  ) -> dict[tuple[str, ...], set[tuple[str, str]]]:
    """Literal label tuples used at two or more call sites, with the ``(module, function)`` sites."""
    by_key: dict[tuple[str, ...], list] = {}
    for module, function, line, literal in found:
        by_key.setdefault(literal, []).append((module, function, line))
    return {key: {(m, f) for m, f, _ in sites} for key, sites in by_key.items()
            if len(sites) > 1 and key}


def _package_sources() -> dict[str, str]:
    return {path.name: path.read_text() for path in sorted(PACKAGE.glob("*.py"))}


def test_bypass_scan_flags_every_bypass_and_passes_the_good_forms() -> None:
    """The scanner flags what it should on hand-written sources (P4 scanner check).

    Reference: source strings with a known verdict. Flagged: ``seed + 1``, ``config.seed + 5``,
    ``np.random.seed(0)``, ``numpy.random.rand``, ``import random``, ``PRNGKey(seed)``,
    ``PRNGKey(7)``, ``PRNGKey(x)`` with ``x`` not a draw, and a name assigned a draw in one place
    and something else in another. Passed: ``PRNGKey(int(rng.integers(0, 2**32)))`` and a name
    assigned only from such a draw in the same function; a type annotation
    ``np.random.Generator``. ``default_rng`` is reported with its enclosing function.
    """
    bad = {
        "plus": "x = seed + 1",
        "plus_attr": "x = config.seed + 5",
        "np_seed": "import numpy as np\nnp.random.seed(0)",
        "np_rand": "import numpy\nnumpy.random.rand(3)",
        "stdlib": "import random",
        "key_seed": "k = PRNGKey(seed)",
        "key_const": "k = PRNGKey(7)",
        "key_name": "def f(x):\n    return PRNGKey(x)",
        "mixed": ("def f(rng):\n    a = int(rng.integers(0, 4))\n    a = 3\n"
                  "    return PRNGKey(a)"),
    }
    for name, source in bad.items():
        assert scan_bypass({name: source})[1], f"{name} was not flagged"
    good = ("import numpy as np\n"
            "def train(rng: np.random.Generator):\n"
            "    a = int(rng.integers(0, 2**32))\n"
            "    k = PRNGKey(a)\n"
            "    return PRNGKey(int(rng.integers(0, 2**32)))\n"
            "def make():\n    return np.random.default_rng(1)\n")
    sites, problems = scan_bypass({"good.py": good})
    assert problems == [] and sites == {("good.py", "make")}


def test_no_bypass_of_make_rng_in_the_package() -> None:
    """P4: ``default_rng(`` only at the four allowed sites; no seed arithmetic; keys are draws.

    Reference: the exact allowlist of the plan (``make_rng``, the integer path of
    ``block_resample_indices``, and the two ``validation.py`` fixtures of DEC-0017 Q7), read from
    the ``ast`` of the package. Tolerance: none (set equality, so a new site and a lost site both
    fail). At least one ``PRNGKey`` is scanned, so the key check cannot pass vacuously.
    """
    sources = _package_sources()
    sites, problems = scan_bypass(sources)
    assert sites == DEFAULT_RNG_ALLOWLIST, sites ^ DEFAULT_RNG_ALLOWLIST
    assert problems == [], problems
    assert "PRNGKey(" in sources["networks.py"]


def test_label_scan_reads_make_rng_and_paired_change_calls() -> None:
    """The label scanner lists literal labels and groups the sites that share them (P5 scanner).

    Reference: hand-written sources. A shared tuple is reported with both sites; a call with
    different labels is not; the tuple of ``_paired_change`` is read as a label; a call with a
    ``*labels`` argument is not listed (its callers are).
    """
    source = ("def a(s):\n    return make_rng(s, 'sys', 'x', 'y')\n"
              "def a2(s):\n    return make_rng(s, 'sys', 'x', 'y')\n"
              "def c(s):\n    return make_rng(s, 'sys', 'z')\n"
              "def d(s, labels):\n    return make_rng(s, *labels)\n"
              "def e(s):\n    return _paired_change(1, 2, s, 0.9, ('sys', 'p', f'{s:g}'), 'n')\n"
              "def f(s):\n    return _paired_change(*u, s, 0.9, ('sys', 'p', f'{s:g}'), 'n')\n")
    found = scan_labels({"m.py": source})
    assert [f[1] for f in found] == ["a", "a2", "c", "e", "f"]
    assert shared_labels(found) == {("sys", "x", "y"): {("m.py", "a"), ("m.py", "a2")},
                                    ("sys", "p", "f'{s:g}'"): {("m.py", "e"), ("m.py", "f")}}


def test_labels_are_shared_only_by_the_documented_pairings() -> None:
    """P5: no literal label tuple is used by two ``make_rng`` call sites except the pairings.

    Reference: the pairing list ``PAIRINGS`` (M4 of the mathematics check), written above. The
    observed shared tuples must equal the list exactly, with the same sites, so adding a
    pairing and losing one both fail. Tolerance: none.
    """
    found = scan_labels(_package_sources())
    assert len(found) >= 30, len(found)  # the scan must see the package's call sites
    assert shared_labels(found) == PAIRINGS


def _label(*keys: object) -> str:
    """The string that ``make_rng`` hashes (written again here, independent of the code)."""
    return "|".join(str(k) for k in keys)


def _full_preset_labels() -> list[str]:
    """Every distinct label string of a full-preset run, enumerated from the configuration."""
    cfg = FULL
    systems = ("lorenz63", "rossler", "chua")
    dims = sorted({cfg.embedding_dim, *cfg.robustness_dims})
    rhos = sorted({*cfg.noise_levels, *cfg.library_sweep_noises, cfg.core_noise})
    labels = set()
    for system in systems:
        labels |= {_label(system, tail) for tail in (
            "library-noise", "misspec", "h2a-initial-segments", "h2a-two-part", "h3b-bootstrap",
            "h3c-ratio", "V4-convergence", "finite-growth", "oracle-pool", "start")}
        labels |= {_label(system, "bootstrap", name) for name in (
            "H1b", "H1c", "H2b-noise", "H2c", "H2d", "Q-N")}
        labels |= {_label(system, "bootstrap", "H1a", f"{rho:g}") for rho in rhos}
        labels |= {_label(system, "bootstrap", "H1d", name) for name in (
            "analog_seed", "estimation_seed", "growth", "nhat")}
        labels |= {_label(system, "bootstrap", "V7", "slope")}
        labels |= {_label(system, "bootstrap", "V7", f"efficiency-{rho:g}") for rho in rhos}
        labels |= {_label(system, tail, f"{rho:g}") for tail in (
            "h2b-library-change", "h2b-curves", "h2e") for rho in rhos}
        for dim in dims:
            labels.add(_label(system, dim, "allocator"))
            labels |= {_label(system, dim, split, purpose)
                       for split in ("construction", "calibration", "test")
                       for purpose in ("oracle", "eval", "verify", "convergence")}
            for delay in range(1, cfg.steps_per_lyapunov + 1):
                labels |= {_label(system, dim, delay, "estimator", f"{rho:g}", width)
                           for rho in rhos for width in cfg.estimator_widths}
    return sorted(labels)


def test_crc32_of_every_full_preset_label_is_distinct() -> None:
    """P5 (tightened by the mathematics check): distinct label strings have distinct crc32.

    Reference: ``zlib.crc32`` on the enumerated strings (independent of ``make_rng``). A crc
    collision would give two ``make_rng`` calls the same stream (the seed enters the generator
    key next to the crc). With about 2400 strings in a space of 2^32 the chance of a collision is
    about 7e-4, so a failure would be a real finding and the test pins the actual strings of the
    full preset. The enumeration is
    a superset of what a run draws (all delays 1 to 30, all noise levels at every site). Also
    checks that ``make_rng`` hashes exactly this string, with a hand key, so the enumeration
    describes the real streams. Tolerance: none.
    """
    labels = _full_preset_labels()
    assert len(labels) > 2000, len(labels)  # 2400 at the time of writing: the scan is not empty
    crcs = [zlib.crc32(label.encode()) for label in labels]
    assert len(set(crcs)) == len(crcs), [
        (a, b) for a, b in itertools.combinations(labels, 2)
        if zlib.crc32(a.encode()) == zlib.crc32(b.encode())][:3]
    seed = 20261005
    mine = make_rng(seed, "lorenz63", 7, 5, "estimator", "0.01", 64).random(4)
    ref = np.random.default_rng([seed, zlib.crc32(b"lorenz63|7|5|estimator|0.01|64")]).random(4)
    assert np.array_equal(mine, ref)
