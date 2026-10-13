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
import pytest

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
    ("bootstrap", "H1b"): {("analysis.py", "h1b_seed_amplifier"),   # CP and PLP
                           ("clip_sensitivity.py", "h1b_part")},    # the clip recomputation
    ("bootstrap", "H2b-noise"): {("analysis.py", "h2b_knob_response"),
                                 ("clip_sensitivity.py", "h2b_noise_part")},
    ("bootstrap", "H2c"): {("analysis.py", "h2c_state_dependence")},  # the three differences
    ("h2a-two-part",): {("analysis.py", "h2a_separation"),
                        ("clip_sensitivity.py", "h2a_parts"),
                        ("experiments.py", "_perturbation_scale_variant")},  # H2a(ii), its variants
    ("h2b-library-change", "f'{rho:g}'"): {("analysis.py", "h2b_knob_response"),
                                           ("clip_sensitivity.py", "h2b_library_part")},
}
"""Literal label tuples that two or more ``make_rng`` call sites share on purpose (M4 of the
mathematics check, extended in review R1 to the clip-sensitivity recomputation, which must draw
the SAME resamples as the verdict it re-reads, otherwise its flags measure resampling noise): the
pairing of the H1b CP and PLP resamples, of the three H2c differences, of H2a(ii) with its Lambda_fin
variant and its clip recomputation, of H2b(i) and H2b(ii) with their clip recomputations. Every
other pairing (H1c, Q-N, the directions across scales, the oracle pool, the estimator and allocator
streams) shares by calling ONE site more than once, which this scan cannot see; ``test_analysis.py``
and ``test_experiments.py`` pin those (P9), and ``test_clip_sensitivity.py`` (T6) pins the
recomputation: no clipped entry gives a delta of exactly 0.0."""


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


SEED_NAMES = frozenset({"seed", "boot_seed", "master_seed"})
"""Names that hold a master seed or a bootstrap seed in the package."""

SEED_CONSUMERS = frozenset({
    "make_rng", "sklearn_seed", "draw_starts", "state_oracles", "_h3b_trees", "fit_regime_tree",
    "qn_regressor", "qn_profile_block", "with_seed", "resolve_dev_seed", "int", "isinstance", "type"})
"""Callees that may receive a master seed (an integer) directly: the labelled-generator factory,
the scikit-learn seed derivation, and the functions whose parameter is the master seed by
design (WU-0002.14). Anything else that receives a seed-named value is a finding."""

PASS_THROUGH = frozenset({
    ("analysis.py", "h2a_initial_segments"), ("analysis.py", "h2a_part_ii"),
    ("analysis.py", "qn_profile_block")})
"""Functions whose ``seed``/``boot_seed`` parameter is a Generator (or the master seed of
``qn_regressor``) and is forwarded; callers pass a ``make_rng(...)`` generator (checked below)."""

BOOTSTRAP_SEED_ARGUMENT = {
    "block_resample_indices": (3, "seed"), "bootstrap_values": (4, "seed"),
    "block_bootstrap_counted": (4, "seed"), "block_bootstrap_dropped": (4, "seed"),
    "block_bootstrap": (4, "seed"), "_boot": (3, "rng"), "h2a_part_ii": (None, "seed"),
    "h2a_initial_segments": (None, "seed"), "qn_profile_block": (None, "boot_seed")}
"""Position and keyword of the generator argument of the bootstrap helpers. A production caller
must pass a ``make_rng(...)`` call or a generator-valued name, never an integer or a seed-named
value: the integer path of ``block_resample_indices`` has no production caller (plan, P4)."""


def _is_seed(node: ast.expr) -> bool:
    """True for a seed-named variable or an attribute named ``seed`` (``config.seed``)."""
    return (isinstance(node, ast.Name) and node.id in SEED_NAMES) or (
        isinstance(node, ast.Attribute) and node.attr == "seed")


def _mentions_seed(node: ast.AST) -> bool:
    """True if a seed-named variable occurs anywhere in the expression."""
    return any(_is_seed(n) for n in ast.walk(node))


def _is_generator_draw(node: ast.expr) -> bool:
    """True for ``int(<expr>.integers(...))``."""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "int" and len(node.args) == 1
            and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Attribute)
            and node.args[0].func.attr == "integers")


def _callee(call: ast.Call) -> str | None:
    func = call.func
    return func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)


def _is_random_attribute(node: ast.AST, roots: tuple[str, ...]) -> bool:
    """True for ``<root>.random`` (``np.random``, ``jax.random``) as an attribute chain."""
    return (isinstance(node, ast.Attribute) and node.attr == "random"
            and isinstance(node.value, ast.Name) and node.value.id in roots)


def scan_bypass(sources: dict[str, str]) -> tuple[set[tuple[str, str]], list[str]]:
    """Find the ``default_rng`` sites and the other bypasses of ``make_rng`` in module sources.

    Findings (the second element): seed arithmetic of any shape and depth (``seed + 1``,
    ``seed * 2 + 1``, ``config.seed - 1``); a seed-named value passed as an argument to a callee
    outside ``SEED_CONSUMERS`` (a pass-through function of ``PASS_THROUGH`` excepted); an integer
    constant or a seed-named value in the generator position of a bootstrap helper (the integer
    path); ``np.random`` attributes other than ``Generator`` and ``default_rng``; ``getattr`` on
    ``np.random``; ``import random``, ``from random import``, ``from numpy.random import``,
    ``from numpy import random``, ``import numpy.random`` and ``from jax import random``;
    ``jax.random.key`` and ``wrap_key_data``; ``PRNGKey`` arguments that are not Generator draws;
    a ``random_state=`` that is not a ``sklearn_seed`` call. Modules named ``seeds.py`` (the seed
    registry) are exempt from the seed-argument and arithmetic rules.

    Returns
    -------
    tuple[set[tuple[str, str]], list[str]]
        The set of ``(module, function)`` that call ``default_rng``, and the findings.
    """
    sites: set[tuple[str, str]] = set()
    problems: list[str] = []
    for module, source in sources.items():
        tree = ast.parse(source)
        owner = _enclosing(tree)
        registry = module == "seeds.py"
        draws: dict[tuple[str, str], bool] = {}  # (function, name) -> assigned only from draws
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                key = (owner[node], node.targets[0].id)
                draws[key] = draws.get(key, True) and _is_generator_draw(node.value)
        for node in ast.walk(tree):
            where = f"{module}:{getattr(node, 'lineno', '?')}"
            if isinstance(node, ast.Call):
                callee = _callee(node)
                here = (module, owner[node])
                if callee == "default_rng":
                    sites.add(here)
                if callee in ("key", "wrap_key_data") and isinstance(node.func, ast.Attribute) \
                        and _is_random_attribute(node.func.value, ("jax",)):
                    problems.append(f"{where} jax.random.{callee}")
                if callee == "getattr" and node.args and any(
                        _is_random_attribute(n, ("np", "numpy", "jax")) for n in ast.walk(node.args[0])):
                    problems.append(f"{where} getattr on a random module")
                if callee == "PRNGKey":
                    arg = node.args[0] if len(node.args) == 1 and not node.keywords else None
                    ok = arg is not None and (
                        _is_generator_draw(arg) or (isinstance(arg, ast.Name)
                                                    and draws.get((owner[node], arg.id), False)))
                    if not ok:
                        problems.append(f"{where} PRNGKey argument is not a Generator draw")
                for kw in node.keywords:
                    if kw.arg == "random_state" and not (
                            isinstance(kw.value, ast.Call) and _callee(kw.value) == "sklearn_seed"):
                        problems.append(f"{where} random_state is not a sklearn_seed call")
                if not registry:
                    direct = [a for a in node.args] + [k.value for k in node.keywords]
                    for arg in direct:
                        if _is_seed(arg) and callee not in SEED_CONSUMERS and here not in PASS_THROUGH \
                                and not (callee == "default_rng" and here in DEFAULT_RNG_ALLOWLIST) \
                                and module != "statistics.py":
                            problems.append(f"{where} seed passed to {callee}")
                    position, keyword = BOOTSTRAP_SEED_ARGUMENT.get(callee, (None, None))
                    given = [k.value for k in node.keywords if k.arg == keyword]
                    if position is not None and len(node.args) > position:
                        given.append(node.args[position])
                    elif callee in BOOTSTRAP_SEED_ARGUMENT and not given:
                        problems.append(f"{where} {callee} without a generator argument")
                    for arg in given:
                        integer = isinstance(arg, ast.Constant) and isinstance(arg.value, int)
                        if integer or (_mentions_seed(arg) and not (
                                isinstance(arg, ast.Call) and _callee(arg) == "make_rng")) and \
                                module != "statistics.py" and here not in PASS_THROUGH:
                            problems.append(f"{where} integer or seed-named generator argument "
                                            f"of {callee}")
            elif (isinstance(node, ast.BinOp) or (isinstance(node, ast.UnaryOp) and isinstance(
                    node.op, (ast.USub, ast.UAdd, ast.Invert)))) and not registry \
                    and _mentions_seed(node):
                problems.append(f"{where} seed arithmetic")
            elif isinstance(node, ast.Attribute) and node.attr not in ("Generator", "default_rng") \
                    and _is_random_attribute(node.value, ("np", "numpy")):
                problems.append(f"{where} np.random.{node.attr}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "random" or alias.name.startswith(("random.", "numpy.random")):
                        problems.append(f"{where} import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module == "random" or node.module.startswith(
                        ("numpy.random", "random."))):
                    problems.append(f"{where} from {node.module} import")
                elif node.module in ("numpy", "jax") and any(a.name == "random" for a in node.names):
                    problems.append(f"{where} from {node.module} import random")
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
    """The scanner flags what it should on hand-written sources (P4 scanner check, review R2).

    Reference: source strings with a known verdict, one per form. Flagged: seed arithmetic of any
    shape (``seed + 1``, ``config.seed + 5``, ``seed * 2 + 1``, ``config.seed - 1``, a seed deep in
    an expression, ``-seed``); ``np.random.seed``, ``numpy.random.rand``, ``getattr(np.random, ...)``;
    ``import random``, ``import numpy.random``, ``from numpy.random import ...``,
    ``from numpy import random``, ``from jax import random``; ``jax.random.key`` and
    ``wrap_key_data``; ``PRNGKey(seed)``, ``PRNGKey(7)``, ``PRNGKey(x)``, a name that is not always
    a draw; an integer or seed-named value in the generator position of a bootstrap helper
    (positional or keyword), a bootstrap helper without one, a seed passed to any other callee;
    ``random_state=0`` and ``random_state=config.seed``. Passed: ``PRNGKey(int(rng.integers(...)))``
    and a name assigned only from such a draw; ``make_rng(config.seed, ...)``, ``sklearn_seed``,
    ``not isinstance(seed, int)``, a bootstrap helper given a ``make_rng`` call or a generator
    name; the annotation ``np.random.Generator``. ``default_rng`` is reported with its enclosing
    function.
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
        # review R2 (WU-0002.14): forms the first version of the scan let through
        "int_seed_to_bootstrap": "def f(c):\n    return block_bootstrap_counted(s, 5, 10, 5, c.seed, .95)",
        "int_literal_to_bootstrap": "def f():\n    return bootstrap_values(s, 5, 10, 5, 7)",
        "int_literal_keyword": "def f():\n    return block_bootstrap(s, 5, 10, 5, seed=7)",
        "seed_keyword_h2a": "def f(c):\n    return h2a_part_ii(w, g, x, n_resamples=1, block=5, seed=c.seed)",
        "boot_seed_keyword": "def f(c):\n    return qn_profile_block(x, boot_seed=c.seed)",
        "no_generator_argument": "def f():\n    return block_bootstrap(s, 5, 10, 5)",
        "seed_to_other_callee": "def f(c):\n    return helper(c.seed)",
        "seed_keyword_other": "def f(c):\n    return helper(x=seed)",
        "jax_key": "import jax\nk = jax.random.key(0)",
        "wrap_key_data": "import jax\nk = jax.random.wrap_key_data(d)",
        "from_numpy_random": "from numpy.random import default_rng as dr",
        "from_numpy_random_generator": "from numpy.random import Generator, PCG64",
        "from_numpy_import_random": "from numpy import random as npr",
        "import_numpy_random": "import numpy.random",
        "from_jax_import_random": "from jax import random",
        "getattr_random": "import numpy as np\nf = getattr(np.random, 'seed')",
        "seed_times_two": "x = seed * 2 + 1",
        "seed_minus_one": "x = config.seed - 1",
        "seed_deep": "x = (3 + (config.seed ^ 5)) % 7",
        "seed_negated": "x = -seed",
        "random_state_const": "M(random_state=0)",
        "random_state_seed": "M(random_state=config.seed)",
    }
    for name, source in bad.items():
        assert scan_bypass({name: source})[1], f"{name} was not flagged"
    good = ("import numpy as np\n"
            "def train(rng: np.random.Generator):\n"
            "    a = int(rng.integers(0, 2**32))\n"
            "    k = PRNGKey(a)\n"
            "    return PRNGKey(int(rng.integers(0, 2**32)))\n"
            "def make():\n    return np.random.default_rng(1)\n"
            # forms that must stay legal
            "def legal(config, seed, system):\n"
            "    rng = make_rng(config.seed, system, 'x')\n"
            "    ok = not isinstance(seed, int)\n"
            "    s = sklearn_seed(seed, 'a')\n"
            "    M(random_state=sklearn_seed(config.seed, 'b'))\n"
            "    return block_bootstrap_counted(f, 5, 10, 5, make_rng(config.seed, system, 'y'), .95)\n"
            "def legal_name(rng):\n    return bootstrap_values(f, 5, 10, 5, rng)\n")
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


def label_templates(sources: dict[str, str]) -> list[tuple[str, str, int, list[ast.expr]]]:
    """Every ``make_rng`` call (and the label tuple of every ``_paired_change`` call): the label
    expressions after the seed, as AST nodes. A ``*labels`` call is skipped (its callers are read)."""
    out = []
    for module, source in sources.items():
        tree = ast.parse(source)
        owner = _enclosing(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = _callee(node)
            if callee == "make_rng" and not any(isinstance(a, ast.Starred) for a in node.args[1:]):
                out.append((module, owner[node], node.lineno, list(node.args[1:])))
            elif callee == "_paired_change":
                tup = next((a.elts for a in node.args if isinstance(a, ast.Tuple)), None)
                if tup is not None:
                    out.append((module, owner[node], node.lineno, list(tup)))
    return out


def string_arguments(sources: dict[str, str], callee: str, index: int) -> set[str]:
    """The string literals at argument ``index`` of every call of ``callee`` in the sources."""
    found = set()
    for source in sources.values():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call) and _callee(node) == callee and len(node.args) > index:
                arg = node.args[index]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.add(arg.value)
    return found


def label_domains(sources: dict[str, str]) -> dict[str, list]:
    """The values each variable part of a label takes in a full-preset run, from the configuration
    and from the literals at the call sites (purposes of ``unit_noise``, labels of ``sklearn_seed``)."""
    from lpcstudy.analysis import H1D_REPORTED, H1D_TESTED
    from lpcstudy.data import SPLITS

    cfg = FULL
    rhos = sorted({*cfg.noise_levels, *cfg.library_sweep_noises, cfg.core_noise})
    return {
        "system": list(cfg.core_systems),
        "embed_dim": sorted({cfg.embedding_dim, *cfg.robustness_dims}),
        "delay": list(range(1, cfg.steps_per_lyapunov + 1)),
        "split": list(SPLITS),
        "purpose": sorted(string_arguments(sources, "unit_noise", 2)),
        "width": list(cfg.estimator_widths),
        "name": [*H1D_TESTED, *H1D_REPORTED],
        "rho": rhos,
        "sklearn": sorted(string_arguments(sources, "sklearn_seed", 1)),
    }


def _domain_of(expr: ast.expr, domains: dict[str, list]) -> list:
    """The domain of one label expression; an unknown expression is an error (never skipped)."""
    text = ast.unparse(expr)
    if isinstance(expr, ast.Constant):
        return [expr.value]
    if isinstance(expr, ast.JoinedStr):
        raise TypeError("f-strings are expanded by _expand")
    if text.endswith("embed_dim"):
        return domains["embed_dim"]
    if text.endswith(".delay"):
        return domains["delay"]
    if text == "label":
        return domains["sklearn"]
    if text in domains:
        return domains[text]
    if text.endswith(("system", "spec.name")):
        return domains["system"]
    raise KeyError(f"no domain for the label part {text!r}: add it to label_domains "
                   "(a new purpose must not be left out of the crc32 check)")


def _expand(parts: list[ast.expr], domains: dict[str, list]) -> list[str]:
    """All label strings of one call site: the product of the domains of its parts."""
    choices = []
    for part in parts:
        if isinstance(part, ast.JoinedStr):
            variants = [""]
            for piece in part.values:
                if isinstance(piece, ast.Constant):
                    variants = [v + piece.value for v in variants]
                else:  # FormattedValue: a noise level formatted with :g
                    assert isinstance(piece, ast.FormattedValue), ast.dump(piece)
                    values = domains["rho"]
                    variants = [v + format(x, "g") for v in variants for x in values]
            choices.append(variants)
        else:
            choices.append(_domain_of(part, domains))
    return [_label(*combo) for combo in itertools.product(*choices)]


def _full_preset_labels() -> list[str]:
    """Every label string that the call sites of the package can produce in a full-preset run,
    derived from the scan of the sources (review R3), not from a hand list."""
    sources = _package_sources()
    domains = label_domains(sources)
    labels: set[str] = set()
    for _, _, _, parts in label_templates(sources):
        labels.update(_expand(parts, domains))
    return sorted(labels)


def test_crc32_of_every_full_preset_label_is_distinct() -> None:
    """P5 (tightened by the mathematics check, review R3): distinct label strings, distinct crc32.

    Reference: ``zlib.crc32`` on the strings (independent of ``make_rng``). The strings come from
    the AST scan of every ``make_rng`` call (and ``_paired_change`` label tuple) of the package,
    each variable part expanded over its domain in the full preset (systems, embedding dimensions
    {5, 7, 10}, delays 1 to 30, splits, widths, noise levels, the H1d names), the purposes of
    ``unit_noise`` and the ``sklearn_seed`` labels read from the call sites, so a new purpose, label
    or site is included by construction, and an expression with no domain fails the test. A crc
    collision would give two ``make_rng`` calls the same stream (the seed enters the generator key
    next to the crc). With about 2500 strings in a space of 2^32 the chance of a collision is
    about 7e-4, so a failure would be a real finding. Tolerance: none.
    """
    labels = _full_preset_labels()
    assert len(labels) > 2400, len(labels)
    for expected in ("lorenz63|7|construction|noise-sensitivity", "sklearn|regime-tree",
                     "start|rossler", "lorenz63|oracle-pool",
                     "chua|10|30|estimator|0.05|128", "rossler|bootstrap|V7|efficiency-0.005"):
        assert expected in labels, expected
    crcs = [zlib.crc32(label.encode()) for label in labels]
    assert len(set(crcs)) == len(crcs), [
        (a, b) for a, b in itertools.combinations(labels, 2)
        if zlib.crc32(a.encode()) == zlib.crc32(b.encode())][:3]
    seed = 20261005
    mine = make_rng(seed, "lorenz63", 7, 5, "estimator", "0.01", 64).random(4)
    ref = np.random.default_rng([seed, zlib.crc32(b"lorenz63|7|5|estimator|0.01|64")]).random(4)
    assert np.array_equal(mine, ref)


def test_label_expansion_flags_an_unknown_part_and_expands_f_strings() -> None:
    """The enumeration fails loudly on a label part it has no domain for (it never skips one), and
    expands a ``{rho:g}`` f-string over the noise levels. Reference: hand-written calls."""
    sources = {"m.py": "def f(s, ctx):\n    return make_rng(s, ctx.spec.name, 'x', mystery)\n"}
    domains = label_domains(_package_sources())
    (_, _, _, parts), = label_templates(sources)
    with pytest.raises(KeyError, match="mystery"):
        _expand(parts, domains)
    (_, _, _, parts), = label_templates(
        {"m.py": "def f(s, system):\n    return make_rng(s, system, f'efficiency-{rho:g}')\n"})
    assert sorted(_expand(parts, domains)) == sorted(
        f"{sys}|efficiency-{rho:g}" for sys in FULL.core_systems
        for rho in sorted({*FULL.noise_levels, *FULL.library_sweep_noises, FULL.core_noise}))


def test_the_start_label_belongs_to_draw_starts_alone() -> None:
    """The label ``"start"`` is used by ``draw_starts`` only, so no other stream shares it.

    Reference: the ``make_rng`` call sites found by the scanner (tested above on hand sources).
    Tolerance: none (exact list).
    """
    sites = [(m, f) for m, f, _, literal in scan_labels(_package_sources()) if "start" in literal]
    assert sites == [("data.py", "draw_starts")]
